r"""stage_d1_s2_loops - D1 STAGE S2 as `docs/cycle27-plan.md` Pre-decided 34 defines it:
THREE empty While loops on `Diagram #686`, each scaffolded `OpCreateEqual_v0` -> `OpStopFromNode_v0`, ONE save.

NO `move_in`, NO queues, NO re-wiring, NO new op, NO new device (34(a)/(b)/(i); Pre-decided 2).
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 No motor, no ASI, no camera, no GUI action. Rig state 조립; this build needs no instrument.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (CLAUDE.md "check what exists first";
`grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `tools/bench/diag_s2_scaffold.py` - cycle 50's MEASURED shape (13 pass / 1 fail, ExecState 1, saved,
    re-read COLD 1 / PRELOADED 1). This stage is that shape times three, so its helpers are IMPORTED rather
    than re-typed: `Preload` `:167`, `fresh` `:155`, `file_facts` `:142`, `census_686` `:198`,
    `candidates_from` `:218`, `try_candidate` `:260`, `read_state` `:343`, `try_save` `:351`. Importing the
    module runs no build (its work is under `if __name__ == "__main__"`), and none of those helpers calls its
    `gate()`, so this file owns every gate it reports.
  * `gscript.loop_in("while", ...)` `tools/gscript.py:1155` - the BUILT While-loop creator.
  * `gscript.save/exec_state/open_panel/close_panel/count/uids/new_since/ref_counts` - built, unchanged.
  * `build_opstopfromnode_v0.loop_end_ref` `:340` - the BUILT conditional-terminal reader (final re-read).
  * `build_d1_v0.diag_index/owner_of` `:357`/`:338`; `bench_prep.labview_handles`; `hash_probe.probe` (34(k)).
  * `diag_d1_execstate_preload.run_condition` `:192` - the BUILT child-process ExecState reader, used ONLY on
    the SAVED file (34(l): an unsaved in-memory edit cannot survive the restart it does).
  * `stage_d1_s1.cold_subvi_table` `:377` / `compare_subvi_tables` `:408` / `TIFF_SUBVI_KEY` `:246` /
    `PIN_SUBVI_ROWS` `:245` / `log_table_diff` `:430` - S1's BUILT, already-FATAL D5 instrument, invoked here
    exactly as `stage_d1_s1.py:727-755` invokes it (Fix A4 below). Importing that module runs no build (its work
    is under `if __name__ == "__main__"`); its ONE module-level side effect, `g._run.__defaults__ = (6.0, 180.0)`,
    is captured and restored so the scaffold half runs on the same timeouts the cycle-50 diagnostic measured.
Nothing new is built.

TWO PRIOR-ART FIXES, both findings ACCEPTED by judgement (cycle 51; review
`archive/peer/2026-09-20-priorart-d1-s2-loops.md`, slugs `contradicted` + `unread-evidence`):
  * FIX A3 (`contradicted`) - every conditional-terminal readback goes through `cond_read()`, which reads
    `OpLoopEndRef_v0`'s FOUR per-property error columns (`err` + `errs`, contract `build_d1_v0.py:848-853`,
    `build_opstopfromnode_v0.py:340-344`). A non-empty column makes the outcome **UNREAD** - a distinct third
    outcome beside pass and FAIL, never a bare value and never a silent FAIL (Pre-decided 14,
    `docs/cycle27-plan.md:147-150`: a value returned beside an error has measured nothing). UNREAD never passes a
    gate. The imported `try_candidate`'s own readback discards those columns, so its `cond_after` is kept as a
    fact and this file's `cond_read` is what every gate scores.
  * FIX A4 (`unread-evidence`) - the SubVI class COUNT is no longer the gate. The gate is S1's SubVI **TABLE**
    comparison against the ORIGINAL (Pre-decided 29(g), `docs/cycle27-plan.md:629-641`, `:790`), because
    `shutil.copy2` silently re-binds 22 SubVI calls and loses 8, which no count can see. The count stays as a
    reported observation.

THE ONE DEVIATION FROM THE DIAGNOSTIC, and it is pre-decided: `PREFERRED` is monkey-patched from the
diagnostic's `(637, 'frame index')` - which 34(l) measured to be NOT a named source terminal on `Diagram #686` -
to the operand that WON there, node **#8486 `x+1`** (Function, Nodes[0], scalar). If the census re-read does not
offer it, `candidates_from` falls back exactly as the diagnostic does (first scalar-shaped named output in census
order) and the log says which was used. Operands are picked BY NAME from the diagram's own output-terminal
census, never by ordinal and never from a wire table (34(c) + 34(l)).

EVERY ADDRESS IS A uid OR AN EXACT NAME, RE-READ IMMEDIATELY BEFORE USE (34(h)): the operand and diagram are
held as uids/names; `diag_index`, the WhileLoop class index and the operand's class index are re-read inside
each iteration, never cached across a mutation.

PREDICTION CONTRACT (each line is a printed GATE; counts are `D1_s1_copy.vi` -> `D1_s2_loops.vi`)
  G1  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859 (hash_probe, read-only).            FATAL
  G2  `claudeDev\D1_s1_copy.vi` md5 3e3d23cefd3a334001aa9d6156bf1aee, 474202 B, BEFORE the copy.     FATAL
  G3  the target copy is byte-identical to it.                                                       FATAL
  G4  baseline class census == Diagram 170 / WhileLoop 3 / SubVI 97 / Comparison 14.                 FATAL
  G5  the operand is a named SCALAR source terminal of a `Diagram #686` node (34(c)).                FATAL
  G6a/b/c   loop k: exactly one new Diagram + one new WhileLoop, owned by `Diagram #686`.            FATAL
  G7a/b/c   loop k: exactly one new Comparison, no op error, and the loop's conditional terminal is
            the SAME uid carrying a NON-ZERO wire that the driving Comparison sources, READ with its
            A3 outcome (pass / FAIL / UNREAD - an UNREAD readback is not a pass).                    FATAL
  G8  final counts: Diagram 173, WhileLoop 6, Comparison 17 (+3), LoopTunnel 135 (+3, one tunnel
      per scaffold - MEASURED `tools/bench/diag_s2_scaffold.json`).                                  FATAL
  G8w Wire 1899 -> 1905 (+2 per scaffold): the delta is REPORTED, never fatal - +2 is derived from a
      ONE-loop measurement, not a three-loop one.                                               non-fatal
  G8s SubVI count still 97: a reported OBSERVATION. The SubVI acceptance gate is G15 (Fix A4).   non-fatal
  G9  all THREE conditional terminals re-read BY UID at the end still carry their recorded wire,
      each with its A3 outcome.                                                                      FATAL
  G10 `ExecState` == 1 before the save, in-instance with the ORIGINAL PRELOADED read-only (34(l)).   FATAL
  G11 `g.save()` returns bytes with default allow_broken=False; `gui_save` is never called (29(g)).  FATAL
  G12 the saved file re-read in a FRESH child process reads COLD 1 and PRELOADED 1 (29(c)).      non-fatal
  G13 no live VI Server reference is left open.                                                  non-fatal
  G14 the ORIGINAL's md5 is unchanged at the end (hash_probe again).                                 FATAL
  G15 FIX A4, the SubVI ACCEPTANCE gate, S1's D5 instrument unchanged: the saved artefact's COLD
      SubVI TABLE equals the ORIGINAL's COLD table MINUS the one key (639, 22700) key-for-key in
      BOTH name and path (97 vs 98 rows), ZERO rows into `claudeDev\background VIs_COPY\`, no empty
      name or path. Sub-results a/b/c and the row-count pins are reported individually; the
      combined verdict is the FATAL line. S2 adds no SubVI, so `expect_missing` is S1's single key.  FATAL
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
import gscript as g                                                              # noqa: E402
import diag_s2_scaffold as D                                                     # noqa: E402
import diag_d1_execstate_preload as D1ES                                         # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
from build_d1_v0 import diag_index, owner_of                                     # noqa: E402
from build_opstopfromnode_v0 import loop_end_ref as LOOP_END_REF                 # noqa: E402
from hash_probe import probe as HASH                                             # noqa: E402
# FIX A4: S1's BUILT SubVI-table instrument, imported, never re-authored. Its module-level
# `g._run.__defaults__ = (6.0, 180.0)` is captured and restored so the scaffold half keeps the timeouts the
# cycle-50 diagnostic ran under; the S1 defaults are re-applied around the G15 block, where they were measured.
_RUN_DEFAULTS_BEFORE_S1 = g._run.__defaults__
from stage_d1_s1 import (cold_subvi_table, compare_subvi_tables, log_table_diff,  # noqa: E402
                         BG_COPY, PIN_SUBVI_ROWS, TIFF_SUBVI_KEY)
_RUN_DEFAULTS_S1 = g._run.__defaults__
g._run.__defaults__ = _RUN_DEFAULTS_BEFORE_S1

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S1_SIZE = D.S1_SIZE
TARGET = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
OUT = os.path.join(ROOT, "tools", "bench", "stage_d1_s2_loops.json")

SIBLING_DIAG_UID = D.SIBLING_DIAG_UID                    # 686
OPERAND = (8486, "x+1")                                  # 34(l): the measured winner, by NAME
LOOP_LOCATIONS = [(2600, 2600), (2600, 3400), (2600, 4200)]   # v7 `:793`, via stage_d1_s2.py:432
BASELINE = {"Diagram": 170, "WhileLoop": 3, "SubVI": 97, "Comparison": 14, "LoopTunnel": 132, "Wire": 1899}
# FATAL contract counts. SubVI and Wire are deliberately ABSENT: SubVI's acceptance gate is G15 (Fix A4) and
# Wire's +6 is derived from a one-loop measurement, so both are reported, not gated fatally.
EXPECTED = {"Diagram": 173, "WhileLoop": 6, "Comparison": 17, "LoopTunnel": 135}
EXPECTED_REPORTED = {"SubVI": 97, "Wire": 1905}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stage": "D1 S2 (Pre-decided 34)", "no_vi_was_run": True,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5}, "s1_artefact": {"path": S1_ARTEFACT},
     "target": {"path": TARGET}, "loops": [], "readings": {}, "saves": {}, "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    (passes if ok else fails).append(name)
    line = "  %s  %s%s" % ("PASS" if ok else "**FAIL**", name, ("  " + detail) if detail else "")
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
    d = dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])
    return d


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def loop_index_of(target, loop_uid):
    """The WhileLoop Traverse index of `loop_uid`, RE-READ at the call site - never cached across a mutation
    (34(h)). `report_all` is the ordered listing every index in this fleet comes from."""
    return [o["uid"] for o in g.report_all(target, "WhileLoop")].index(loop_uid)


def cond_read(tag, target, loop_uid):
    """FIX A3: ONE conditional-terminal readback through `OpLoopEndRef_v0`, scored on its FOUR per-property
    ERROR COLUMNS as well as its values.

    `LOOP_END_REF` returns `err` (the op's `error out`) and `errs` (the concatenation of `LoopEndRefErr`,
    `IsSourceErr`, `ConnWireErr`, `WireUIDErr` - `build_d1_v0.py:848-853`, re-exported at
    `build_opstopfromnode_v0.py:340-344`). Pre-decided 14 (`docs/cycle27-plan.md:147-150`) binds: a value returned
    beside an error has MEASURED NOTHING. So a non-empty column makes this reading **UNREAD** - a distinct third
    outcome beside pass and FAIL - and an UNREAD reading never satisfies a gate, however plausible its uids look.
    (The imported `try_candidate` discards these columns; that is exactly the prior-art finding `contradicted`.)"""
    li = loop_index_of(target, loop_uid)
    r = LOOP_END_REF(target, li)
    e1, e2 = (r.get("err") or "").strip(), (r.get("errs") or "").strip()
    rec = {"tag": tag, "loop_uid": loop_uid, "loop_index": li, "cond_term_uid": r.get("cond_term_uid"),
           "cond_wire_uid": r.get("cond_wire_uid"), "is_source": r.get("is_source"), "err": e1, "errs": e2,
           "outcome": "UNREAD" if (e1 or e2) else "READ"}
    R.setdefault("cond_reads", []).append(rec)
    fact("A3 %s: outcome %s - WhileLoop #%d (index %d) conditional terminal #%s, wire %s, is_source %r; "
         "err %r errs %r" % (tag, rec["outcome"], loop_uid, li, rec["cond_term_uid"], rec["cond_wire_uid"],
                             rec["is_source"], e1[:120], e2[:120]))
    return rec


def counts(tag, target):
    c = {k: g.count(target, k) for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")}
    fact("class census %s: %r" % (tag, c))
    return c


def main():
    print("=== stage_d1_s2_loops  %s   (D1 S2, Pre-decided 34; NO VI IS RUN, 34(f))"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])

    o = probe("G1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("G1 the ORIGINAL exists and its md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("G2 the S1 artefact BEFORE the copy", S1_ARTEFACT)
    gate("G2 the S1 artefact md5 == %s and size == %d B" % (S1_MD5, S1_SIZE),
         s.get("md5") == S1_MD5 and s.get("size") == str(S1_SIZE), "md5 %s size %s" % (s.get("md5"), s.get("size")))

    D.fresh("G2b")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(TARGET):
        os.remove(TARGET)
        fact("removed a pre-existing %s before the copy" % os.path.basename(TARGET))
    shutil.copy2(S1_ARTEFACT, TARGET)
    t = probe("G3 the target copy", TARGET)
    gate("G3 the target copy is byte-identical to the S1 artefact", t.get("md5") == S1_MD5, t.get("md5", "?"))

    with D.Preload("P"):
        g.open_panel(TARGET)                      # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        R["before_census"] = counts("BEFORE any edit", TARGET)
        gate("G4 baseline census == %r" % BASELINE,
             all(R["before_census"][k] == v for k, v in BASELINE.items()),
             repr({k: R["before_census"][k] for k in BASELINE}))

        # ---- the operand: BY NAME, from Diagram #686's own output-terminal census (34(c)/34(l))
        print("\n--- census of Diagram #%d - nodes and their OUTPUT terminal names" % SIBLING_DIAG_UID, flush=True)
        D.PREFERRED = OPERAND                     # 34(l): the measured winner replaces the diagnostic's #637
        _d686, _w, rows = D.census_686(TARGET)
        cands = D.candidates_from(rows, TARGET)
        gate("G5 Diagram #%d offers a named scalar-shaped SOURCE terminal to compare (34(c))" % SIBLING_DIAG_UID,
             bool(cands), "0 candidates")
        cand = cands[0]
        R["operand"] = cand
        fact("OPERAND: node #%d Nodes[%d] (%s) terminal %r - %s%s"
             % (cand["uid"], cand["node_index"], cand["class_guess"], cand["name"], cand["why"],
                "" if (cand["uid"], cand["name"]) == OPERAND else "  ** NOT the pre-decided #%d %r **" % OPERAND))

        # ---- three loops, each created then scaffolded; every index re-read inside the iteration (34(h))
        for k, loc in enumerate(LOOP_LOCATIONS):
            tag = "abc"[k]
            print("\n--- loop %s of 3 at %r on Diagram #%d" % (tag, loc, SIBLING_DIAG_UID), flush=True)
            d686 = diag_index(TARGET, SIBLING_DIAG_UID)        # re-read, never cached across a mutation
            dg0, wl0 = g.uids(TARGET, "Diagram"), g.uids(TARGET, "WhileLoop")
            g.loop_in("while", TARGET, d686, loc)
            nd = g.new_since(TARGET, "Diagram", dg0)
            nw = g.new_since(TARGET, "WhileLoop", wl0)
            gate("G6%s loop %s: exactly one new Diagram and one new WhileLoop" % (tag, tag),
                 len(nd) == 1 and len(nw) == 1, "+%d diagrams, +%d while loops" % (len(nd), len(nw)))
            loop_uid, body_uid = nw[0]["uid"], nd[0]["uid"]
            _c, own = owner_of(TARGET, loop_uid)
            gate("G6%s loop %s is owned by Diagram #%d" % (tag, tag, SIBLING_DIAG_UID), own == SIBLING_DIAG_UID,
                 "owner %r" % (own,))
            fact("loop %s: WhileLoop #%d, body Diagram #%d, at %r, owner Diagram #%s"
                 % (tag, loop_uid, body_uid, loc, own))
            # FIX A3, the BEFORE reading: an UNWIRED conditional terminal legitimately errors on the
            # `Connected Wire` read (error 1055 - there is no wire to return a reference for,
            # `build_d1_v0.py:867-869`), so UNREAD is the EXPECTED outcome here and is recorded, not gated.
            cond_read("loop %s BEFORE the scaffold (UNREAD is expected: no wire yet)" % tag, TARGET, loop_uid)
            att = D.try_candidate(cand, TARGET, loop_uid, body_uid, d686)
            rec = {"tag": tag, "location": list(loc), "loop_uid": loop_uid, "body_uid": body_uid,
                   "owner": own, "attempt": att}
            R["loops"].append(rec)
            gate("G7%s loop %s: one new Comparison, no op error" % (tag, tag),
                 bool(att["created_comparison"]) and not att["create_error"] and len(att["created_comparison"]) == 1,
                 "created %r error %r" % (att["created_comparison"], att["create_error"]))
            cr = cond_read("loop %s AFTER the scaffold" % tag, TARGET, loop_uid)     # FIX A3
            rec["cond_after_a3"] = cr
            cmp_uid = (att["wire_identity"] or {}).get("comparison_uid")
            gate("G7%s loop %s: conditional terminal #%s carries wire %s that Comparison #%s sources, A3 "
                 "outcome %s" % (tag, tag, cr["cond_term_uid"], cr["cond_wire_uid"], cmp_uid, cr["outcome"]),
                 bool(att["ok"]) and cr["outcome"] == "READ" and bool(cr["cond_wire_uid"]),
                 "stop error %r; A3 %s err %r errs %r"
                 % (att["stop_error"], cr["outcome"], cr["err"][:80], cr["errs"][:80]))

        # ---- the contract counts
        print("\n--- the contract counts", flush=True)
        R["after_census"] = counts("AFTER the three loops", TARGET)
        for key, want in EXPECTED.items():
            gate("G8 %s == %d (%d -> %d)" % (key, want, BASELINE[key], want),
                 R["after_census"][key] == want, "observed %d" % R["after_census"][key])
        # REPORTED, never fatal: Wire's +2-per-scaffold is derived from a ONE-loop measurement, and SubVI's
        # acceptance gate is G15's TABLE comparison (Fix A4), not this count.
        gate("G8w Wire %d -> %d (delta +%d, predicted +6 from a one-loop measurement) - REPORTED"
             % (BASELINE["Wire"], R["after_census"]["Wire"], R["after_census"]["Wire"] - BASELINE["Wire"]),
             R["after_census"]["Wire"] == EXPECTED_REPORTED["Wire"],
             "observed %d, predicted %d" % (R["after_census"]["Wire"], EXPECTED_REPORTED["Wire"]), fatal=False)
        gate("G8s SubVI count still %d (an OBSERVATION; the acceptance gate is G15's table, Fix A4)"
             % EXPECTED_REPORTED["SubVI"], R["after_census"]["SubVI"] == EXPECTED_REPORTED["SubVI"],
             "observed %d" % R["after_census"]["SubVI"], fatal=False)

        # ---- G9: all three conditional terminals RE-READ BY UID, after every mutation is done
        print("\n--- re-reading all three conditional terminals BY UID (34(h))", flush=True)
        ok9 = True
        for rec in R["loops"]:
            now = cond_read("loop %s FINAL" % rec["tag"], TARGET, rec["loop_uid"])     # FIX A3
            was = rec["cond_after_a3"]
            same = (now["cond_term_uid"] == was["cond_term_uid"]
                    and now["cond_wire_uid"] == was["cond_wire_uid"] and now["cond_wire_uid"])
            rec["cond_final"] = {"cond_term_uid": now["cond_term_uid"], "cond_wire_uid": now["cond_wire_uid"],
                                 "outcome": now["outcome"], "err": now["err"], "errs": now["errs"],
                                 "comparison_uid": (rec["attempt"]["wire_identity"] or {}).get("comparison_uid")}
            fact("loop %s FINAL: WhileLoop #%d (index %d) conditional terminal #%s, wire %s, Comparison #%s, "
                 "A3 outcome %s" % (rec["tag"], rec["loop_uid"], now["loop_index"], now["cond_term_uid"],
                                    now["cond_wire_uid"], rec["cond_final"]["comparison_uid"], now["outcome"]))
            ok9 = ok9 and bool(same) and now["outcome"] == "READ"
        gate("G9 all three conditional terminals still carry their recorded wire, read back by uid, every A3 "
             "outcome READ (an UNREAD readback is not a pass)", ok9, repr([r["cond_final"] for r in R["loops"]]))

        # ---- G10 ExecState, then the ONE save
        print("\n--- ExecState with the ORIGINAL preloaded (34(l)), then the ONE save", flush=True)
        es = D.read_state("pre_save_in_instance_preloaded", TARGET)
        R["readings"]["pre_save_in_instance_preloaded"] = es
        gate("G10 ExecState == 1 before the save (1 = runnable, 0 = broken)", es == 1, "exec_state = %r" % es)
        sv = D.try_save("s2", TARGET)
        R["saves"]["s2"] = sv
        gate("G11 g.save() returned bytes with allow_broken=False (gui_save never called)",
             sv["exception"] is None and sv["returned_bytes"], "exception %r returned %r"
             % (sv["exception"], sv["returned_bytes"]))
        try:
            g.close_panel(TARGET)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))

    # ---- G12: the saved file, re-read in a FRESH child process, cold and preloaded (29(c))
    print("\n--- child-process re-reads of the SAVED artefact (cold, then preloaded)", flush=True)
    for tag, pre in (("S2-COLD", False), ("S2-PRELOAD", True)):
        try:
            res = D1ES.run_condition(tag, TARGET, pre)
            R["readings"][tag] = res.get("execstate")
            fact("CHILD %s (preload=%s): ExecState %r, rc %r"
                 % (tag, pre, res.get("execstate"), res.get("child_rc", res.get("rc"))))
        except Exception as e:                                                    # noqa: BLE001
            R["readings"][tag] = "RAISED %s: %s" % (type(e).__name__, e)
            fact("CHILD %s raised %s: %s" % (tag, type(e).__name__, e))
    gate("G12 the saved artefact reads COLD 1 / PRELOADED 1 in a fresh process",
         R["readings"].get("S2-COLD") == 1 and R["readings"].get("S2-PRELOAD") == 1,
         "COLD %r PRELOADED %r" % (R["readings"].get("S2-COLD"), R["readings"].get("S2-PRELOAD")), fatal=False)
    probe("the saved artefact, final", TARGET)

    # ---- G15: FIX A4 - the SubVI ACCEPTANCE gate is S1's TABLE comparison against the ORIGINAL, not a count.
    # Pre-decided 29(g) (`docs/cycle27-plan.md:629-641`, `:790`): `shutil.copy2` silently re-binds 22 SubVI calls
    # into `claudeDev\background VIs_COPY\` and loses 8 - a class COUNT cannot see any of that, so the ORIGINAL's
    # COLD table is the acceptance reference. Invoked exactly as `stage_d1_s1.py:727-755` invokes it: one
    # condition per child process and per fresh LabVIEW instance, NO preload anywhere, this parent holding no COM
    # proxy across it. S2 deletes nothing and adds no SubVI, so `expect_missing` is S1's single key (639, 22700).
    print("\n--- G15 (Fix A4): the SAVED artefact's COLD SubVI TABLE against the ORIGINAL's COLD table", flush=True)
    g.reset()
    g._run.__defaults__ = _RUN_DEFAULTS_S1              # the timeouts S1 measured this instrument under
    s2_tbl, s2_rec = cold_subvi_table("G15a-S2LOOPS-COLD", TARGET)
    orig_tbl, orig_rec = cold_subvi_table("G15b-ORIG-COLD", ORIGINAL)
    cmp_s2 = compare_subvi_tables(s2_tbl, orig_tbl, {TIFF_SUBVI_KEY})
    R["subvi_census"] = {"s2_artefact": s2_rec, "original": orig_rec}
    R["subvi_compare_s2_vs_original"] = cmp_s2
    R["subvi_expected_missing_key"] = list(TIFF_SUBVI_KEY)
    fact("G15 row counts: S2 artefact %s vs ORIGINAL %s (expected %d vs %d); the one key S1 removed and S2 keeps "
         "removed is (diagram %d, node %d) = #22700 IMAQ Write TIFF File 2; the bait directory is %s"
         % (s2_rec["n_rows"], orig_rec["n_rows"], PIN_SUBVI_ROWS - 1, PIN_SUBVI_ROWS,
            TIFF_SUBVI_KEY[0], TIFF_SUBVI_KEY[1], BG_COPY))
    if not cmp_s2["equal"]:
        log_table_diff("G15 S2 artefact vs ORIGINAL", cmp_s2)
    gate("G15-i the ORIGINAL's COLD SubVI table has %d rows" % PIN_SUBVI_ROWS,
         orig_rec["n_rows"] == PIN_SUBVI_ROWS, "%s rows" % orig_rec["n_rows"], fatal=False)
    gate("G15-ii the S2 artefact's COLD SubVI table has %d rows" % (PIN_SUBVI_ROWS - 1),
         s2_rec["n_rows"] == PIN_SUBVI_ROWS - 1, "%s rows" % s2_rec["n_rows"], fatal=False)
    ok_a, ok_b, ok_c = cmp_s2["equal"], s2_rec["into_background_vis_copy"] == 0, s2_rec["empty_rows"] == 0
    gate("G15a the S2 table is EXACTLY the ORIGINAL's table minus (%d, %d), every surviving row identical in BOTH "
         "name and path" % TIFF_SUBVI_KEY, ok_a,
         "missing=%d extra=%d changed=%d not_deleted=%s bad_key=%s"
         % (len(cmp_s2["missing"]), len(cmp_s2["extra"]), len(cmp_s2["changed"]), cmp_s2["not_deleted"],
            cmp_s2["expected_key_absent_from_reference"]), fatal=False)
    gate("G15b ZERO rows of the S2 table point into claudeDev\\background VIs_COPY\\", ok_b,
         "%d rows, first keys %s" % (s2_rec["into_background_vis_copy"], s2_rec["background_vis_copy_keys"]),
         fatal=False)
    gate("G15c no row of the S2 table has an empty name or an empty path", ok_c,
         "%d rows, first keys %s" % (s2_rec["empty_rows"], s2_rec["empty_keys"]), fatal=False)
    dump()
    gate("G15 FATAL the saved S2 artefact's SubVI table is accepted against the ORIGINAL (a AND b AND c)",
         ok_a and ok_b and ok_c, "a=%s b=%s c=%s" % (ok_a, ok_b, ok_c))


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
        fact("refs at end: %r (every reference this script opened is closed by its opener)" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("G13 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        oe = probe("G14 ORIGINAL after the run", ORIGINAL)
        R["original"]["md5_after"] = oe.get("md5")
        if oe.get("md5") != ORIG_MD5:
            gate("G14 the ORIGINAL's md5 is unchanged", False, oe.get("md5", "?"), fatal=False)
            rc = 1
        else:
            gate("G14 the ORIGINAL's md5 is unchanged", True, oe.get("md5", "?"), fatal=False)
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== ARTEFACT: %s" % TARGET, flush=True)
        print("=== NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
