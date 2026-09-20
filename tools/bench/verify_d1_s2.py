r"""verify_d1_s2 - READ-ONLY verification of the artefact cycle 51's build LEFT ON DISK.

🔴 THIS IS A DIAGNOSTIC, NOT A RECIPE. It lives in `tools/bench/`, it produces READINGS
(`tools/bench/verify_d1_s2.json` + this log), and it must never be moved under `tools/recipes/`.
🔴 IT BUILDS NOTHING AND CHANGES NOTHING: no `loop_in`, no `move_in`, no queue, no re-wiring, no new op, no
`g.save()`, no `gui_save`. The only writes are to the two files above. NO VI IS RUN (Pre-decided 34(f)); the
only VIs that execute are the BUILT reader op VIs - that is what scripting is. No motor, no ASI, no camera, no
GUI action. `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are opened READ-ONLY and never saved; the
ORIGINAL is never opened by this file at all except inside the BUILT child helpers, read-only, and its md5 is
probed at both ends.

WHY IT EXISTS: cycle 51 ran `tools/recipes/stage_d1_s2_loops.py`, reached `g.save()` and recorded
`claudeDev\D1_s2_loops.vi` md5 6ff19497f2309e007a214660bb64b911 / 475707 B with G8/G8w/G8s/G9/G10/G11 PASS; the
session then EXITED and killed the child in its own cold re-read, so G12 (child COLD/PRELOAD) and G15 (the SubVI
TABLE acceptance gate) never ran. That recipe is NOT re-run here. This reads the file it left.

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "check what exists before creating anything"; checked
`grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `hash_probe.probe` (34(k)) - the read-only md5/sha256/size probe.
  * `diag_s2_scaffold.fresh` `:155` / `.file_facts` `:142` - the restart and the file-fact recorder.
  * `build_opstopfromnode_v0.loop_end_ref` `:340` - the BUILT conditional-terminal reader, which echoes the
    loop's OWN uid back beside the terminal it read, and `wire_source` `:350` (`OpWireSource_v5`, 12/12) - the
    BUILT "which object DRIVES this wire" reader, UID-addressed.
  * `build_d1_v0.owner_of` `:338` / `diag_index` `:357` / `terms_of` `:375` - the BUILT ownership/parent
    traversal and per-node terminal reader.
  * `stage_d1_s2_loops.cond_read`'s A3 SEMANTICS (`tools/recipes/stage_d1_s2_loops.py:177`) - re-implemented
    here in four lines rather than imported, because importing that module would import a RECIPE into a
    diagnostic; the scoring rule is identical and is stated in `cond_read` below.
  * `diag_d1_execstate_preload.run_condition` `:192` - the BUILT child-process ExecState reader (34(l): it
    restarts LabVIEW, so it can only read a file ON DISK - which is exactly this case).
  * `stage_d1_s1.cold_subvi_table` `:377` / `compare_subvi_tables` `:408` / `log_table_diff` `:430` /
    `TIFF_SUBVI_KEY` `:246` / `PIN_SUBVI_ROWS` `:245` / `BG_COPY` `:244` - S1's BUILT, already-FATAL D5
    instrument (29(g)), invoked exactly as `stage_d1_s2_loops.py:356-388` invokes it.
  * `bench_prep.labview_handles` - the handle reading.
Nothing new is built. No op is created (Pre-decided 2; user 2026-09-18 08:53).

ADDRESSING RULE (34(h)): every Traverse index is re-read from `report_all` immediately before the call that uses
it; only uids and exact names are carried. LOOP IDENTITY IS NEVER TAKEN FROM AN ARRAY INDEX - a loop is named by
its uid, and the owner of a conditional terminal is established by `loop_end_ref`'s echoed `LoopUID` and by
`owner_of(term_uid)`, i.e. by parent traversal.

PREDICTION CONTRACT (each line is a printed GATE; only V0 and the file-existence gates are FATAL, because this
is a measurement and every later reading is wanted even when an earlier one fails)
  V0  the ORIGINAL, `D1_s1_copy.vi` and `D1_s2_loops.vi` all exist.                                    FATAL
  V1  ORIGINAL md5 == 2a78e17c449cacdaf5da389818526859.                                                FATAL
  V2  `D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911 and size == 475707 B.
  V3  `D1_s1_copy.vi` md5 == 3e3d23cefd3a334001aa9d6156bf1aee and size == 474202 B.
  V4  S1 census == Diagram 170 / WhileLoop 3 / SubVI 97 / Comparison 14 / LoopTunnel 132 / Wire 1899.
  V5  S2 census == Diagram 173 / WhileLoop 6 / SubVI 97 / Comparison 17 / LoopTunnel 135 / Wire 1905.
  V6  the WhileLoop uid set of S2 CONTAINS S1's, and the difference is EXACTLY 3 uids.
  V6b all 3 new WhileLoops are owned by `Diagram #686`; the 3 shared ones keep their S1 owners.
  V7  each of the three recorded conditional terminals #23080 / #23246 / #23456 is owned by a WhileLoop that is
      NEW in S2 (never by a loop that already existed in S1). ⚠️ THE SHARPEST READING: cycle 51's log named
      loop b `WhileLoop #10170 (index 1)`, a pre-existing-looking uid.
  V8  every WhileLoop present in BOTH files reports the SAME conditional terminal uid and the SAME wire uid in
      both, with an A3 outcome of READ on both sides.
  V9  the Comparison uid difference S1 -> S2 is EXACTLY 3, and each new Comparison sources the wire sitting on
      exactly one of the three conditional terminals.
  V10 the three conditional terminals, re-read BY UID through `cond_read`, are READ (not UNREAD, not absent)
      and carry a NON-ZERO wire.
  V11 `D1_s2_loops.vi` re-read in a FRESH child process reads COLD 1 and PRELOADED 1 (29(c)/34(l)).
  V12 the saved artefact's COLD SubVI TABLE equals the ORIGINAL's COLD table MINUS the single key
      (639, 22700), key-for-key in BOTH name and path; zero rows into `claudeDev\background VIs_COPY\`; no
      empty name or path (29(g), Fix A4 - the COUNT is never the acceptance reference).
  V13 no live VI Server reference is left open; handles before/after are recorded.
  V14 the ORIGINAL's md5 is unchanged at the end.                                                      FATAL
"""
import json
import os
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
import diag_d1_execstate_preload as D1ES                                          # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import owner_of, diag_index, terms_of                            # noqa: E402
from build_opstopfromnode_v0 import loop_end_ref as LOOP_END_REF, wire_source      # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402
_RUN_DEFAULTS_BEFORE_S1 = g._run.__defaults__
from stage_d1_s1 import (cold_subvi_table, compare_subvi_tables, log_table_diff,  # noqa: E402
                         BG_COPY, PIN_SUBVI_ROWS, TIFF_SUBVI_KEY)
_RUN_DEFAULTS_S1 = g._run.__defaults__
g._run.__defaults__ = _RUN_DEFAULTS_BEFORE_S1

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1 = D.S1_ARTEFACT                                       # claudeDev\D1_s1_copy.vi
S1_MD5, S1_SIZE = D.S1_MD5, D.S1_SIZE
S2 = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5, S2_SIZE = "6ff19497f2309e007a214660bb64b911", 475707      # STATUS owner_c51m2 / the cycle-51 log
OUT = os.path.join(HERE, "verify_d1_s2.json")

SIBLING_DIAG_UID = D.SIBLING_DIAG_UID                    # 686
COND_TERMS = (23080, 23246, 23456)                       # the three RECORDED conditional terminals
CENSUS_CLASSES = ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")
S1_CENSUS = {"Diagram": 170, "WhileLoop": 3, "SubVI": 97, "Comparison": 14, "LoopTunnel": 132, "Wire": 1899}
S2_CENSUS = {"Diagram": 173, "WhileLoop": 6, "SubVI": 97, "Comparison": 17, "LoopTunnel": 135, "Wire": 1905}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "no_vi_was_run": True, "nothing_was_built_or_saved": True,
     "files": {}, "s1": {}, "s2": {}, "join": {}, "readings": {}, "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
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
    d = dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])
    return d


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def cond_read(tag, target, loop_uid):
    """ONE conditional-terminal readback through `OpLoopEndRef_v0`, scored on its FOUR per-property ERROR COLUMNS
    as well as on its values - `stage_d1_s2_loops.py:177`'s A3 rule, verbatim in meaning: Pre-decided 14
    (`docs/cycle27-plan.md:147-150`) binds that a value returned beside an error has MEASURED NOTHING, so a
    non-empty column makes the outcome **UNREAD**, a third outcome that no gate accepts, never a bare value.
    The loop's Traverse index is re-read from `report_all` HERE, immediately before the call (34(h)), and the op
    echoes the loop's own `LoopUID` back, so the (loop -> conditional terminal) pairing below is an OWNERSHIP
    reading, never an array-index guess."""
    order = [o["uid"] for o in g.report_all(target, "WhileLoop")]
    li = order.index(loop_uid)
    r = LOOP_END_REF(target, li)
    e1, e2 = (r.get("err") or "").strip(), (r.get("errs") or "").strip()
    rec = {"tag": tag, "asked_loop_uid": loop_uid, "loop_index_at_call": li,
           "echoed_loop_uid": r.get("loop_uid"), "cond_term_uid": r.get("cond_term_uid"),
           "cond_wire_uid": r.get("cond_wire_uid"), "is_source": r.get("is_source"), "err": e1, "errs": e2,
           "outcome": "UNREAD" if (e1 or e2) else "READ",
           "uid_echo_ok": r.get("loop_uid") == loop_uid}
    fact("A3 %s: %s - asked WhileLoop #%d (index %d at call), op echoed LoopUID #%s%s; conditional terminal "
         "#%s, wire %s, is_source %r; err %r errs %r"
         % (tag, rec["outcome"], loop_uid, li, rec["echoed_loop_uid"],
            "" if rec["uid_echo_ok"] else "  ** ECHO MISMATCH **", rec["cond_term_uid"], rec["cond_wire_uid"],
            rec["is_source"], e1[:100], e2[:100]))
    return rec


def owner(target, uid):
    """Parent traversal, with the error kept rather than swallowed."""
    try:
        cls, ou = owner_of(target, uid, strict=True)
        return {"uid": uid, "owner_class": cls, "owner_uid": ou, "error": None}
    except Exception as e:                                                        # noqa: BLE001
        return {"uid": uid, "owner_class": None, "owner_uid": None, "error": "%s: %s" % (type(e).__name__, e)}


def read_one(tag, path, key):
    """Everything this file reads out of ONE .vi, read-only: census, WhileLoop identity + ownership + conditional
    terminals, Comparison identity. The panel is opened (the full diagram load a terminal read needs) and closed;
    nothing is saved."""
    print("\n--- %s: reading %s READ-ONLY (no edit, no save)" % (tag, os.path.basename(path)), flush=True)
    rec = R[key]
    g.open_panel(path)
    time.sleep(1.0)
    rec["census"] = {c: g.count(path, c) for c in CENSUS_CLASSES}
    fact("%s class census: %r" % (tag, rec["census"]))

    loops = [o["uid"] for o in g.report_all(path, "WhileLoop")]
    rec["whileloop_uids_report_order"] = loops
    fact("%s WhileLoop uids, in `report_all` order (the order every Traverse index in this fleet comes from): %r"
         % (tag, loops))
    rec["loops"] = {}
    for u in loops:
        o = owner(path, u)
        c = cond_read("%s loop #%d" % (tag, u), path, u)
        rec["loops"][str(u)] = {"uid": u, "owner": o, "cond": c}
        fact("%s WhileLoop #%d: owner %s#%s%s; conditional terminal #%s wire %s (%s)"
             % (tag, u, o["owner_class"], o["owner_uid"],
                "  [on Diagram #%d]" % SIBLING_DIAG_UID if o["owner_uid"] == SIBLING_DIAG_UID else "",
                c["cond_term_uid"], c["cond_wire_uid"], c["outcome"]))

    rec["comparison_uids"] = sorted(o["uid"] for o in g.report_all(path, "Comparison"))
    fact("%s Comparison uids (%d): %r" % (tag, len(rec["comparison_uids"]), rec["comparison_uids"]))
    try:
        g.close_panel(path)
    except Exception as e:                                                        # noqa: BLE001
        fact("%s: close_panel raised %s: %s" % (tag, type(e).__name__, e))
    return rec


def main():
    print("=== verify_d1_s2  %s   (READ-ONLY verification of cycle 51's artefact; NO VI IS RUN, 34(f))"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; cycle 51's client was KILLED)"
         % R["handles"]["before"])

    # ---- (a) the three files
    print("\n--- (a) hash_probe on the three files (read-only, 34(k))", flush=True)
    o = probe("ORIGINAL", ORIGINAL)
    s1 = probe("S1 claudeDev\\D1_s1_copy.vi", S1)
    s2 = probe("S2 claudeDev\\D1_s2_loops.vi", S2)
    R["files"] = {"original": o, "s1": s1, "s2": s2}
    gate("V0 all three files exist", o.get("exists") == "1" and s1.get("exists") == "1"
         and s2.get("exists") == "1", "orig %s s1 %s s2 %s" % (o.get("exists"), s1.get("exists"),
                                                               s2.get("exists")), fatal=True)
    gate("V1 ORIGINAL md5 == %s" % ORIG_MD5, o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    gate("V2 S2 md5 == %s and size == %d B" % (S2_MD5, S2_SIZE),
         s2.get("md5") == S2_MD5 and s2.get("size") == str(S2_SIZE),
         "md5 %s size %s" % (s2.get("md5"), s2.get("size")))
    gate("V3 S1 md5 == %s and size == %d B" % (S1_MD5, S1_SIZE),
         s1.get("md5") == S1_MD5 and s1.get("size") == str(S1_SIZE),
         "md5 %s size %s" % (s1.get("md5"), s1.get("size")))

    # ---- (c)/(d)/(e): one fresh instance per file; never two copies of the main VI in one instance
    D.fresh("F1 (before reading S1)")
    fact("handles after the restart: %r" % labview_handles())
    read_one("S1", S1, "s1")
    gate("V4 S1 census == %r" % S1_CENSUS,
         all(R["s1"]["census"].get(k) == v for k, v in S1_CENSUS.items()),
         repr({k: R["s1"]["census"].get(k) for k in S1_CENSUS}))

    D.fresh("F2 (before reading S2)")
    fact("handles after the restart: %r" % labview_handles())
    read_one("S2", S2, "s2")
    gate("V5 S2 census == %r  (the class census re-read FROM THE SAVED FILE)" % S2_CENSUS,
         all(R["s2"]["census"].get(k) == v for k, v in S2_CENSUS.items()),
         repr({k: R["s2"]["census"].get(k) for k in S2_CENSUS}))

    # ---- (d) LOOP IDENTITY
    print("\n--- (d) LOOP IDENTITY: the WhileLoop uid sets, their difference, and who owns each conditional "
          "terminal", flush=True)
    s1_loops = set(R["s1"].get("whileloop_uids_report_order") or [])
    s2_loops = set(R["s2"].get("whileloop_uids_report_order") or [])
    new_loops = sorted(s2_loops - s1_loops)
    gone_loops = sorted(s1_loops - s2_loops)
    shared = sorted(s1_loops & s2_loops)
    R["join"]["whileloops"] = {"s1": sorted(s1_loops), "s2": sorted(s2_loops), "only_in_s2": new_loops,
                               "only_in_s1": gone_loops, "in_both": shared}
    fact("WhileLoop uids  S1 %r  |  S2 %r" % (sorted(s1_loops), sorted(s2_loops)))
    fact("DIFFERENCE: only in S2 %r ; only in S1 %r ; in both %r" % (new_loops, gone_loops, shared))
    gate("V6 S2 contains every S1 WhileLoop and adds EXACTLY 3", len(new_loops) == 3 and not gone_loops,
         "+%d new %r, -%d missing %r" % (len(new_loops), new_loops, len(gone_loops), gone_loops))
    owners_new = {u: R["s2"]["loops"][str(u)]["owner"] for u in new_loops}
    gate("V6b all 3 new WhileLoops are owned by Diagram #%d" % SIBLING_DIAG_UID,
         bool(new_loops) and all(v["owner_uid"] == SIBLING_DIAG_UID for v in owners_new.values()),
         repr({u: (v["owner_class"], v["owner_uid"], v["error"]) for u, v in owners_new.items()}))
    same_owner = {u: (R["s1"]["loops"][str(u)]["owner"]["owner_uid"],
                      R["s2"]["loops"][str(u)]["owner"]["owner_uid"]) for u in shared}
    gate("V6c the 3 pre-existing WhileLoops keep their S1 owners",
         all(a == b for a, b in same_owner.values()), repr(same_owner))

    # which WhileLoop OWNS each recorded conditional terminal - BY OWNERSHIP, never by array index
    print("\n--- (d) ownership of the three RECORDED conditional terminals %r" % (COND_TERMS,), flush=True)
    R["join"]["cond_term_ownership"] = {}
    for t in COND_TERMS:
        by_loop = [u for u in sorted(s2_loops)
                   if R["s2"]["loops"][str(u)]["cond"]["cond_term_uid"] == t]
        direct = owner(S2, t)
        chain = owner(S2, direct["owner_uid"]) if direct.get("owner_uid") else {"owner_class": None,
                                                                                "owner_uid": None,
                                                                                "error": "no first owner"}
        rec = {"cond_term_uid": t, "loops_reporting_it": by_loop,
               "owner_of_terminal": direct, "owner_of_that_owner": chain,
               "is_new_loop": bool(by_loop) and all(u in new_loops for u in by_loop)}
        R["join"]["cond_term_ownership"][str(t)] = rec
        fact("conditional terminal #%d: reported by WhileLoop(s) %r (%s); owner_of(#%d) = %s#%s, whose owner is "
             "%s#%s%s" % (t, by_loop, "NEW in S2" if rec["is_new_loop"] else "** NOT a new loop **", t,
                          direct["owner_class"], direct["owner_uid"], chain.get("owner_class"),
                          chain.get("owner_uid"),
                          ("; owner_of error %s" % direct["error"]) if direct["error"] else ""))
    gate("V7 each recorded conditional terminal %r is owned by a WhileLoop that is NEW in S2" % (COND_TERMS,),
         all(R["join"]["cond_term_ownership"][str(t)]["is_new_loop"] for t in COND_TERMS),
         repr({t: R["join"]["cond_term_ownership"][str(t)]["loops_reporting_it"] for t in COND_TERMS}))

    # every WhileLoop in BOTH files, side by side
    print("\n--- (d) the loops present in BOTH files, conditional terminal and wire side by side", flush=True)
    side = {}
    for u in shared:
        a = R["s1"]["loops"][str(u)]["cond"]
        b = R["s2"]["loops"][str(u)]["cond"]
        side[str(u)] = {"s1": {k: a[k] for k in ("cond_term_uid", "cond_wire_uid", "outcome", "err", "errs")},
                        "s2": {k: b[k] for k in ("cond_term_uid", "cond_wire_uid", "outcome", "err", "errs")},
                        "identical": (a["cond_term_uid"] == b["cond_term_uid"]
                                      and a["cond_wire_uid"] == b["cond_wire_uid"])}
        fact("SHARED WhileLoop #%d:  S1 terminal #%s wire %s (%s)   |   S2 terminal #%s wire %s (%s)   =>  %s"
             % (u, a["cond_term_uid"], a["cond_wire_uid"], a["outcome"], b["cond_term_uid"], b["cond_wire_uid"],
                b["outcome"], "IDENTICAL" if side[str(u)]["identical"] else "** DIFFERENT **"))
    R["join"]["shared_loop_conditionals"] = side
    gate("V8 every WhileLoop present in both files has the same conditional terminal and wire in both, both READ",
         bool(side) and all(v["identical"] and v["s1"]["outcome"] == "READ" and v["s2"]["outcome"] == "READ"
                            for v in side.values()), repr(side))

    # ---- (e) Comparison
    print("\n--- (e) Comparison: the uid difference, and which conditional terminal each new Equal? drives",
          flush=True)
    c1, c2 = set(R["s1"].get("comparison_uids") or []), set(R["s2"].get("comparison_uids") or [])
    new_cmp, gone_cmp = sorted(c2 - c1), sorted(c1 - c2)
    R["join"]["comparisons"] = {"s1": sorted(c1), "s2": sorted(c2), "only_in_s2": new_cmp,
                                "only_in_s1": gone_cmp, "drives": {}}
    fact("Comparison uids: S1 %d, S2 %d; only in S2 %r; only in S1 %r" % (len(c1), len(c2), new_cmp, gone_cmp))
    gate("V9a the Comparison uid difference S1 -> S2 is exactly 3", len(new_cmp) == 3 and not gone_cmp,
         "+%d %r -%d %r" % (len(new_cmp), new_cmp, len(gone_cmp), gone_cmp))
    cond_wire_by_term = {R["s2"]["loops"][str(u)]["cond"]["cond_term_uid"]:
                         (u, R["s2"]["loops"][str(u)]["cond"]["cond_wire_uid"]) for u in sorted(s2_loops)}
    g.open_panel(S2)
    time.sleep(1.0)
    for cu in new_cmp:
        o = owner(S2, cu)
        row = {"comparison_uid": cu, "owner": o, "source_wires": [], "drives_cond_term": None,
               "drives_loop": None, "error": None}
        try:
            di = diag_index(S2, o["owner_uid"])
            t = terms_of(S2, di, cu, fresh=True)
            row["terminals"] = {str(i): {"name": nm, "is_source": bool(src), "wire": wv}
                                for i, (nm, src, wv) in t.items()}
            row["source_wires"] = sorted({wv for _i, (_nm, src, wv) in t.items() if src and wv})
        except Exception as e:                                                    # noqa: BLE001
            row["error"] = "%s: %s" % (type(e).__name__, e)
        for term_uid, (loop_uid, wire_uid) in cond_wire_by_term.items():
            if wire_uid and wire_uid in row["source_wires"]:
                row["drives_cond_term"], row["drives_loop"] = term_uid, loop_uid
        R["join"]["comparisons"]["drives"][str(cu)] = row
        fact("new Comparison #%d: owner %s#%s; source wires %r => drives conditional terminal #%s of WhileLoop "
             "#%s%s" % (cu, o["owner_class"], o["owner_uid"], row["source_wires"], row["drives_cond_term"],
                        row["drives_loop"], ("; error %s" % row["error"]) if row["error"] else ""))
    gate("V9b each new Comparison drives exactly one of the three recorded conditional terminals",
         bool(new_cmp) and sorted(r["drives_cond_term"] for r in
                                  R["join"]["comparisons"]["drives"].values()
                                  if r["drives_cond_term"]) == sorted(COND_TERMS),
         repr({k: (v["drives_cond_term"], v["drives_loop"])
               for k, v in R["join"]["comparisons"]["drives"].items()}))

    # ---- (f) the three conditional terminals re-read BY UID, with the A3 error columns
    print("\n--- (f) the three recorded conditional terminals re-read by uid, A3 semantics "
          "(`stage_d1_s2_loops.py:177`)", flush=True)
    R["join"]["cond_reread"] = {}
    for t in COND_TERMS:
        holders = R["join"]["cond_term_ownership"][str(t)]["loops_reporting_it"]
        if not holders:
            R["join"]["cond_reread"][str(t)] = {"status": "ABSENT",
                                                "detail": "no WhileLoop of S2 reports conditional terminal #%d"
                                                          % t}
            fact("conditional terminal #%d: ABSENT - no WhileLoop in the saved file reports it" % t)
            continue
        cr = cond_read("FINAL by-uid #%d" % t, S2, holders[0])
        ws = []
        if cr["cond_wire_uid"]:
            try:
                ws = wire_source(S2, cr["cond_wire_uid"])
            except Exception as e:                                                # noqa: BLE001
                ws = [{"error": "%s: %s" % (type(e).__name__, e)}]
        cr["wire_source_rows"] = ws
        srcs = [r for r in ws if isinstance(r, dict) and r.get("is_source")]
        cr["driven_by"] = [(r.get("owner_cls"), r.get("owner_uid")) for r in srcs]
        R["join"]["cond_reread"][str(t)] = cr
        fact("conditional terminal #%d: outcome %s, wire %s, DRIVEN BY %r (OpWireSource_v5, UID-addressed)"
             % (t, cr["outcome"], cr["cond_wire_uid"], cr["driven_by"]))
    gate("V10 all three conditional terminals read back READ with a non-zero wire",
         all(R["join"]["cond_reread"].get(str(t), {}).get("outcome") == "READ"
             and R["join"]["cond_reread"].get(str(t), {}).get("cond_wire_uid") for t in COND_TERMS),
         repr({t: (R["join"]["cond_reread"].get(str(t), {}).get("outcome"),
                   R["join"]["cond_reread"].get(str(t), {}).get("cond_wire_uid")) for t in COND_TERMS}))
    try:
        g.close_panel(S2)
    except Exception as e:                                                        # noqa: BLE001
        fact("close_panel(S2) raised %s: %s" % (type(e).__name__, e))
    dump()

    # ---- (b) the child-process ExecState readings, COLD and with the ORIGINAL PRELOADED
    print("\n--- (b) child-process ExecState of the SAVED D1_s2_loops.vi: COLD, then ORIGINAL PRELOADED",
          flush=True)
    g.reset()
    for tag, pre in (("VERIFY-S2-COLD", False), ("VERIFY-S2-PRELOAD", True)):
        try:
            res = D1ES.run_condition(tag, S2, pre)
            R["readings"][tag] = res.get("execstate")
            fact("CHILD %s (preload=%s): ExecState %r, rc %r" % (tag, pre, res.get("execstate"),
                                                                 res.get("child_rc", res.get("rc"))))
        except Exception as e:                                                    # noqa: BLE001
            R["readings"][tag] = "RAISED %s: %s" % (type(e).__name__, e)
            fact("CHILD %s raised %s: %s" % (tag, type(e).__name__, e))
    gate("V11 the saved artefact reads COLD 1 / PRELOADED 1 in a fresh child process",
         R["readings"].get("VERIFY-S2-COLD") == 1 and R["readings"].get("VERIFY-S2-PRELOAD") == 1,
         "COLD %r PRELOADED %r" % (R["readings"].get("VERIFY-S2-COLD"),
                                   R["readings"].get("VERIFY-S2-PRELOAD")))
    dump()

    # ---- (g) the COLD SubVI TABLE, S2 against the ORIGINAL (29(g), Fix A4 - never the count)
    print("\n--- (g) the COLD SubVI TABLE of D1_s2_loops.vi against the ORIGINAL's (29(g); the COUNT is an "
          "observation, the TABLE is the acceptance reference)", flush=True)
    g.reset()
    g._run.__defaults__ = _RUN_DEFAULTS_S1
    s2_tbl, s2_rec = cold_subvi_table("V12a-S2LOOPS-COLD", S2)
    orig_tbl, orig_rec = cold_subvi_table("V12b-ORIG-COLD", ORIGINAL)
    cmp_s2 = compare_subvi_tables(s2_tbl, orig_tbl, {TIFF_SUBVI_KEY})
    R["subvi_census"] = {"s2_artefact": s2_rec, "original": orig_rec}
    R["subvi_compare_s2_vs_original"] = cmp_s2
    fact("V12 row counts: S2 artefact %s vs ORIGINAL %s (expected %d vs %d); the one key S1 removed and S2 keeps "
         "removed is (diagram %d, node %d) = #22700 IMAQ Write TIFF File 2; the bait directory is %s"
         % (s2_rec["n_rows"], orig_rec["n_rows"], PIN_SUBVI_ROWS - 1, PIN_SUBVI_ROWS,
            TIFF_SUBVI_KEY[0], TIFF_SUBVI_KEY[1], BG_COPY))
    if not cmp_s2["equal"]:
        log_table_diff("V12 S2 artefact vs ORIGINAL", cmp_s2)
    gate("V12-i the ORIGINAL's COLD SubVI table has %d rows" % PIN_SUBVI_ROWS,
         orig_rec["n_rows"] == PIN_SUBVI_ROWS, "%s rows" % orig_rec["n_rows"])
    gate("V12-ii the S2 artefact's COLD SubVI table has %d rows" % (PIN_SUBVI_ROWS - 1),
         s2_rec["n_rows"] == PIN_SUBVI_ROWS - 1, "%s rows" % s2_rec["n_rows"])
    ok_a, ok_b, ok_c = cmp_s2["equal"], s2_rec["into_background_vis_copy"] == 0, s2_rec["empty_rows"] == 0
    gate("V12a the S2 table is EXACTLY the ORIGINAL's minus (%d, %d), every surviving row identical in BOTH name "
         "and path" % TIFF_SUBVI_KEY, ok_a,
         "missing=%d extra=%d changed=%d not_deleted=%s bad_key=%s"
         % (len(cmp_s2["missing"]), len(cmp_s2["extra"]), len(cmp_s2["changed"]), cmp_s2["not_deleted"],
            cmp_s2["expected_key_absent_from_reference"]))
    gate("V12b ZERO rows of the S2 table point into claudeDev\\background VIs_COPY\\", ok_b,
         "%d rows, first keys %s" % (s2_rec["into_background_vis_copy"], s2_rec["background_vis_copy_keys"]))
    gate("V12c no row of the S2 table has an empty name or an empty path", ok_c,
         "%d rows, first keys %s" % (s2_rec["empty_rows"], s2_rec["empty_keys"]))
    gate("V12 the saved S2 artefact's SubVI TABLE is accepted against the ORIGINAL (a AND b AND c)",
         ok_a and ok_b and ok_c, "a=%s b=%s c=%s" % (ok_a, ok_b, ok_c))
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
        gate("V13 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        try:
            oe = probe("V14 ORIGINAL after the run", ORIGINAL)
            R["original_md5_after"] = oe.get("md5")
            if not gate("V14 the ORIGINAL's md5 is unchanged", oe.get("md5") == ORIG_MD5, oe.get("md5", "?")):
                rc = 1
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  V14 could not re-probe the ORIGINAL: %s: %s" % (type(e).__name__, e), flush=True)
            fails.append("V14 re-probe raised")
            rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== NOTHING WAS BUILT, EDITED OR SAVED; NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no "
              "GUI action.", flush=True)
        sys.exit(rc)
