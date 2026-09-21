"""DIAGNOSTIC diag_c75_m3a3_endpoints - MEASUREMENT ONLY for stage M3a-3's two consumer rows.

WHAT THIS IS NOT. It mutates nothing, saves nothing, creates no op / verb / device / recipe. It COPIES
the M3a-2 artefact to a unique scratch name, reads the SCRATCH, DELETES the scratch in the same run,
and re-reads the artefact's md5 to prove it is byte-unchanged. The artefact is BROKEN BY DESIGN and is
NEVER RUN and NEVER OPENED (plan item 34(f)). Per Pre-decided 63 a measurement-only diagnostic GATES ON
HYGIENE ONLY: every measurement below is a FACT line and CANNOT fail the run.

PRIOR ART, CHECKED BEFORE A LINE WAS WRITTEN (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/diag_c74_m3a2_verify.py` - THE WORKING PATTERN for exactly this shape (copy -> read ->
    delete -> re-hash, anchored at register uids). This file follows it and adds no new mechanism.
  * `tools/bench/diag_c73_m3a2_rows.log:42-57` ALREADY carries the 15-slot register census of the OLD
    loop #637 (it was read on the M3a-1 artefact). Those lines are quoted in the summary and the census
    is re-read here only because the BED IS A DIFFERENT FILE (M3a-2, md5 3842f5e6...).
  * `tools/gscript.py` - every reader this needs exists: `shift_reg_left` :816, `node_terms_uid` :955,
    `report_all` :502, `node_labels`, `count` :1035, `exec_state` :2007, `ensure_loaded` :1298,
    `ref_counts` :233. NOTHING NEW IS BUILT.
  * `tools/recipes/build_d1_m3a1.py` - `find_node` :541, `terms_at` :500, `term_state` :524,
    `node_view` :572, `pd85_violations` :811 are IMPORTED, not re-written.
  * `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - the only by-UID walk of a
    WIRE's terminals (repaired 2026-09-22: indicators scrubbed, all error outs read, uid echo required).
  * `tools/recipes/build_d1_v0.py` - `owner_of` :338 (strict uid echo) and `diag_index` :357.

WHAT IT MEASURES (M1..M8 of the cycle-65 material brief). All FACTS, no expectations compared:
  M1  loop #637's registers: the PAIRING and machine-read LABELS of #4256 / #4274 / #4334 / #4344.
  M2  the two consumer NETS - EVERY terminal on wire 4859 and on wire 7506, counted BEFORE any class
      filter (Pre-decided 77), with the SOURCE and SINK counts stated.
  M3  the owning Diagram (uid + traverse index) of #7202, #7468, wires 4859/7506, border #23032, and
      registers #23868 / #23895.
  M4  the two NEW RIGHT registers: label, terminal count, and per terminal index/name/is_source/wire.
  M5  ADDRESSABILITY: for #23868 OUTER, #23895 OUTER, Global #7202 t0 'Focus position' and
      FlatSequenceInnerTunnel #7468 - is each reachable as Diagram(idx).Nodes[n].Terminals[t], with n
      and t RESOLVED LIVE BY UID in this run (never carried from a census - that is what broke T2c2),
      or NOT FOUND after an exhaustive Nodes[] walk.
  M6  #7468's owner object (uid + class).
  M8  ExecState, handles at both ends, refs opened/closed/live, the artefact md5 re-read, the four
      standing pins, scratch deleted.
  (M7 - the verb signatures - is read statically off our own source and is NOT measured here.)

PREDICTION CONTRACT (the hygiene gates; these are the ONLY things that can FAIL)
  H1  the artefact reads md5 3842f5e6f128226235dc78353f26ef44 BEFORE anything is opened
  H2  the four standing pins (ORIGINAL, S1, S2, THE BED) still read their recorded md5
  H3  the scratch copy starts byte-identical to the artefact
  H4  the scratch is DELETED and is no longer on disk at the end
  H5  the artefact re-reads md5 3842f5e6... AFTER the run (it was never opened)
  H6  every VI Server reference this run opened is closed (ref_counts live == 0)

NOT DECIDED HERE. No row table, no verb choice, no recipe written or edited. The judgement session
decides all of that from these facts.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")

ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi")
ARTEFACT_MD5 = "3842f5e6f128226235dc78353f26ef44"
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C75SCRATCH_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c75_m3a3_endpoints.json")

TOP = 0
D686 = 686                 # the diagram said to carry both loop borders and all four wires
LOOP_OLD = 637             # the ORIGINAL While loop
LOOP_NEW = 23032           # the NEW While loop - M3a-1's registers live on its border
OLD_UIDS = (4256, 4274, 4334, 4344)
NEW_RIGHT = (23868, 23895)
CONSUMER_WIRES = (4859, 7506)
GLOBAL_UID = 7202
FSIT_UID = 7468
REG_PROBE_MAX = 16
WALK_N = 10

T0 = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "artefact": ARTEFACT,
     "artefact_md5_pin": ARTEFACT_MD5, "scratch": SCRATCH,
     "task": "MEASUREMENT ONLY for stage M3a-3 (the two downstream consumer rows). Hygiene gates only "
             "(Pre-decided 63); every measurement is a FACT and cannot fail the run.",
     "verification_level": "STRUCTURAL, never functional - nothing is run (34(f))",
     "read_only": "the artefact is copied to a unique scratch; the scratch is read and deleted in this "
                  "same run; the artefact is never opened and its md5 is re-read at the end.",
     "no_new_op": True, "no_new_verb": True, "no_new_device": True, "no_new_checker": True,
     "no_recipe_written": True, "mutates_nothing": True,
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py is not called",
     "handles": {}, "hash_probe": [], "M1": {}, "M2": {}, "M3": {}, "M4": {}, "M5": {}, "M6": {}}


def gate(name, ok, detail=""):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(line):
    print("\n---------- %s" % line, flush=True)


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


# ============================================================================ [0] files only
def phase_0():
    head("[0] FILES ONLY, ZERO LabVIEW - the md5 pins, then the mandatory pre-batch restart")
    R["handles"]["before"] = labview_handles()
    fact("M8 LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500 - a FACT, never a gate)"
         % (R["handles"]["before"],))
    pr = probe_hash("H1 THE ARTEFACT BEFORE", ARTEFACT)
    gate("H1 the artefact reads its pinned md5 %s BEFORE anything is opened" % ARTEFACT_MD5[:8],
         pr.get("md5") == ARTEFACT_MD5, "%r" % (pr.get("md5"),))
    for tag, path, pin in PINS:
        p2 = probe_hash("H2 %s" % tag, path)
        gate("H2 %s md5 == its pin %s" % (tag, pin[:8]), p2.get("md5") == pin, "%r" % (p2.get("md5"),))
    D.fresh("[0] pre-batch LabVIEW restart (STATUS: 42,297 handles at the last exit)")
    R["handles"]["after_restart"] = labview_handles()
    fact("M8 LabVIEW handles AFTER the restart: %r" % (R["handles"]["after_restart"],))
    dump()


# ============================================================================ [1] the scratch
def phase_1_scratch():
    head("[1] THE SCRATCH COPY - the artefact itself is never opened")
    shutil.copy2(ARTEFACT, SCRATCH)
    time.sleep(0.4)
    pr = probe_hash("[1] the scratch straight after the copy", SCRATCH)
    gate("H3 the scratch starts byte-identical to the artefact", pr.get("md5") == ARTEFACT_MD5,
         "%r vs %r" % (pr.get("md5"), ARTEFACT_MD5))
    t0 = time.time()
    _, err = safe("[1] ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("[1] ensure_loaded(scratch) took %.1f s%s"
         % (time.time() - t0, (" ERROR " + err) if err else ""))
    es, _ = safe("[1] exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state"] = es
    fact("M8 the scratch reads ExecState %r - A FACT ONLY. This artefact is BROKEN BY DESIGN and is "
         "never run (34(f)); nothing here is gated on it or reasoned from it." % (es,))
    cnt = {}
    for c in ("Node", "Wire", "LeftShiftRegister", "RightShiftRegister"):
        cnt[c], _ = safe("[1] count(%r)" % c, lambda cc=c: g.count(SCRATCH, cc))
    R["counts"] = cnt
    fact("[1] narrow class counts on the scratch: %r" % (cnt,))
    di, derr = safe("[1] diag_index(#%d)" % D686, lambda: diag_index(SCRATCH, D686))
    R["d686_index"] = di
    fact("M3 Diagram #%d -> traverse index %r%s" % (D686, di, (" ; " + derr) if derr else ""))
    dump()
    return [di, TOP] if di is not None else [TOP]


# ============================================================================ helpers
def loop_index_of(uid, tag):
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(SCRATCH, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d ; %d WhileLoop row(s))%s"
         % (tag, idx, echo, uid, len(rows or []), (" ; " + err) if err else ""))
    return idx if echo == uid else None


def reg_table(loop_index, tag, cap=REG_PROBE_MAX):
    """Every shift register of one loop: the RIGHT register's uid/class/OUTER/INSIDE and the same for
    its LEFT partner (shift_reg_left / OpShiftRegs_v1). Stops at the first slot that errors. THIS IS
    THE ANCHOR - pairing is read here, never inferred from uid ordering or uid arithmetic."""
    out = []
    for k in range(cap):
        sr, err = safe("%s shift_reg_left(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg_left(SCRATCH, loop_index, kk))
        if err or not sr:
            fact("%s reg_index=%d -> READ STOPS HERE: %s" % (tag, k, err or "no row returned"))
            break
        left = sr.get("left") or {}
        row = {"reg_index": k, "right_uid": sr.get("uid"), "right_class": sr.get("class"),
               "right_out": sr.get("out"), "right_inside": sr.get("inside"),
               "left_uid": left.get("uid"), "left_class": left.get("class"),
               "left_out": left.get("out"), "left_inside": left.get("inside"),
               "left_uids": sr.get("left_uids"), "op_errors": sr.get("errors")}
        out.append(row)
        fact("%s reg%-2d RIGHT #%-6r %-20r outer=%r | LEFT #%-6r %-20r outer=%r | errors=%r"
             % (tag, k, row["right_uid"], row["right_class"], row["right_out"], row["left_uid"],
                row["left_class"], row["left_out"], row["op_errors"]))
        if row["op_errors"] or row["right_uid"] in (None, 0):
            break
    return out


def wire_census(wire_uid, tag, n=WALK_N):
    """EVERY terminal on one wire, by UID. Counted BEFORE any class filter (Pre-decided 77), with the
    Pre-decided 85 identity precondition reported per walk (recip == queried uid on every real-owner
    row). A walk with violations > 0 is REPORTED and never used."""
    rec = {"wire": wire_uid, "rows": [], "error": ""}
    walk, err = safe("%s OpWireSource_v5(UID 2 = %d)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(SCRATCH, int(wire_uid), n=n), [])
    rec["error"] = err
    walk = walk or []
    rec["rows_total_before_any_filter"] = len(walk)
    for t in walk:
        rec["rows"].append(t)
        if t.get("owner_uid"):
            fact("    %s w%-6d t%-2r is_source=%-5r owner_class=%-26r owner_uid=%-7r recip=%r"
                 % (tag, wire_uid, t.get("i"), t.get("is_source"), t.get("owner_class"),
                    t.get("owner_uid"), t.get("recip")))
        else:
            fact("    %s w%-6d t%-2r NO OWNER (reader null padding) err=%r"
                 % (tag, wire_uid, t.get("i"), (t.get("err") or "")[:110]))
    real = [t for t in walk if t.get("owner_uid")]
    bad = M.pd85_violations(wire_uid, walk)
    srcs = [t for t in real if t.get("is_source")]
    sinks = [t for t in real if not t.get("is_source")]
    rec["real_owner_rows"] = len(real)
    rec["pd85_violations"] = len(bad)
    rec["sources"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid")) for t in srcs]
    rec["sinks"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid")) for t in sinks]
    fact("M2 wire %d: %d row(s) TOTAL before any class filter, %d with a real owner, PD85 violations %d"
         % (wire_uid, len(walk), len(real), len(bad)))
    fact("M2 wire %d: %d SOURCE terminal(s) %r ; %d SINK terminal(s) %r"
         % (wire_uid, len(srcs), rec["sources"], len(sinks), rec["sinks"]))
    if bad:
        fact("M2 wire %d: THIS WALK IS NOT BELIEVED - PD85 rows %r"
             % (wire_uid, [(t.get("i"), t.get("owner_uid"), t.get("recip")) for t in bad]))
    return rec


# ============================================================ [2] M1 - the OLD loop's registers
def phase_m1():
    head("[2] M1 - the OLD loop #637's register PAIRING and LABELS, read off the machine")
    li = loop_index_of(LOOP_OLD, "M1")
    R["M1"]["loop_index"] = li
    if li is None:
        fact("M1 loop #%d NOT RESOLVED - UNMEASURABLE here" % LOOP_OLD)
        dump()
        return {}
    tbl = reg_table(li, "M1 loop#637")
    R["M1"]["registers"] = tbl
    fact("M1 loop #%d carries %d shift register slot(s); RIGHT uids %r ; LEFT uids %r"
         % (LOOP_OLD, len(tbl), [r["right_uid"] for r in tbl], [r["left_uid"] for r in tbl]))
    pairing = {}
    for uid in OLD_UIDS:
        hit = next((r for r in tbl if r["right_uid"] == uid), None)
        side = "RIGHT"
        if hit is None:
            hit = next((r for r in tbl if r["left_uid"] == uid), None)
            side = "LEFT"
        if hit is None:
            pairing[uid] = {"found": False}
            fact("M1 uid #%d: NOT in loop #%d's live register table - UNMEASURABLE from this loop"
                 % (uid, LOOP_OLD))
            continue
        partner = hit["left_uid"] if side == "RIGHT" else hit["right_uid"]
        term = hit["right_out"] if side == "RIGHT" else hit["left_out"]
        rec = {"found": True, "reg_index": hit["reg_index"], "side": side, "partner_uid": partner,
               "class": hit["right_class"] if side == "RIGHT" else hit["left_class"],
               "label_read_off_the_machine": (term or {}).get("name"),
               "outer_is_source": (term or {}).get("is_source"),
               "outer_wire": (term or {}).get("wire"),
               "owner_loop_uid": LOOP_OLD}
        pairing[uid] = rec
        fact("M1 #%d is the %s member of reg_index %d on loop #%d ; class %r ; its PARTNER is #%r ; "
             "LABEL read off the machine %r ; OUTER is_source=%r wire=%r"
             % (uid, side, hit["reg_index"], LOOP_OLD, rec["class"], partner,
                rec["label_read_off_the_machine"], rec["outer_is_source"], rec["outer_wire"]))
    R["M1"]["pairing"] = pairing
    visa = [u for u in OLD_UIDS if (pairing.get(u) or {}).get("label_read_off_the_machine")
            in ("Outgoing Handle", "VISA out")]
    pos = [u for u in OLD_UIDS if (pairing.get(u) or {}).get("label_read_off_the_machine")
           == "position [internal units]"]
    fact("M1 ANSWER, from LABELS and wires read on the machine (never from uid ordering): the uids "
         "labelled for the VISA session are %r and the uids labelled for the position are %r" % (visa, pos))
    dump()
    return pairing


# ============================================================ [3] M2 - the two consumer nets
def phase_m2():
    head("[3] M2 - the two consumer NETS, FULL terminal census each (count before any class filter)")
    for w in CONSUMER_WIRES:
        R["M2"][str(w)] = wire_census(w, "M2 net")
    dump()


# ============================================================ [4] M3 - owner diagrams
def phase_m3(hints):
    head("[4] M3 - the owning Diagram of every endpoint, uid-echoed")
    diags, err = safe("M3 report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    by_uid = {d["uid"]: d["i"] for d in (diags or [])}
    R["M3"]["diagram_rows"] = len(diags or [])
    fact("M3 Diagram census: %d row(s)%s ; Diagram #%d sits at traverse index %r"
         % (len(diags or []), (" ; " + err) if err else "", D686, by_uid.get(D686)))
    targets = [("Global #%d" % GLOBAL_UID, GLOBAL_UID),
               ("FlatSequenceInnerTunnel #%d" % FSIT_UID, FSIT_UID),
               ("Wire #%d" % CONSUMER_WIRES[0], CONSUMER_WIRES[0]),
               ("Wire #%d" % CONSUMER_WIRES[1], CONSUMER_WIRES[1]),
               ("WhileLoop border #%d" % LOOP_NEW, LOOP_NEW),
               ("RightShiftRegister #%d" % NEW_RIGHT[0], NEW_RIGHT[0]),
               ("RightShiftRegister #%d" % NEW_RIGHT[1], NEW_RIGHT[1])]
    rows = []
    for label, uid in targets:
        (cls, ouid), oerr = safe("M3 owner_of(#%d)" % uid, lambda u=uid: owner_of(SCRATCH, u),
                                 (None, None))
        tidx = by_uid.get(ouid) if cls == "Diagram" else None
        rec = {"label": label, "uid": uid, "owner_class": cls, "owner_uid": ouid,
               "owner_traverse_index": tidx, "on_d686": (ouid == D686), "error": oerr}
        rows.append(rec)
        fact("M3 %-38s owner %r #%r ; traverse index %r ; on Diagram #%d? %r%s"
             % (label, cls, ouid, tidx, D686, ouid == D686, (" ; " + oerr) if oerr else ""))
    R["M3"]["owners"] = rows
    onD686 = [r["label"] for r in rows if r["on_d686"]]
    notD686 = [(r["label"], r["owner_class"], r["owner_uid"]) for r in rows if not r["on_d686"]]
    fact("M3 ANSWER: %d of %d endpoints are owned by Diagram #%d -> %r ; NOT on #%d -> %r"
         % (len(onD686), len(rows), D686, onD686, D686, notD686))
    # the border node's own diagram, resolved by the census that finds it (never by owner_of alone)
    loc, terms = M.node_view(SCRATCH, LOOP_NEW, hints, "M3 border #%d" % LOOP_NEW, quiet=True)
    f = loc.get("found") or {}
    R["M3"]["border_node"] = {"diagram_index": f.get("diagram_index"), "diagram_uid": f.get("diagram_uid"),
                              "nodes_index": f.get("nodes_index"), "uid_echo": loc.get("uid_echo"),
                              "label": f.get("label"), "terminal_count": len(terms)}
    fact("M3 border #%d located by Nodes[] census: Diagram idx %r (uid #%r), Nodes[%r], uid echo %r, "
         "label %r, %d terminal(s)"
         % (LOOP_NEW, f.get("diagram_index"), f.get("diagram_uid"), f.get("nodes_index"),
            loc.get("uid_echo"), f.get("label"), len(terms)))
    dump()
    return terms


# ============================================================ [5] M4 - the NEW right registers
def phase_m4():
    head("[5] M4 - the two NEW RIGHT registers #23868 / #23895, every terminal")
    li = loop_index_of(LOOP_NEW, "M4")
    R["M4"]["loop_index"] = li
    if li is None:
        fact("M4 loop #%d NOT RESOLVED - UNMEASURABLE here" % LOOP_NEW)
        dump()
        return
    tbl = reg_table(li, "M4 loop#23032")
    R["M4"]["registers"] = tbl
    out = {}
    for uid in NEW_RIGHT:
        hit = next((r for r in tbl if r["right_uid"] == uid), None)
        if hit is None:
            out[uid] = {"found": False}
            fact("M4 RIGHT register #%d NOT in loop #%d's live table - UNMEASURABLE" % (uid, LOOP_NEW))
            continue
        terms = []
        o = hit["right_out"] or {}
        terms.append({"index": "OUTER", "name": o.get("name"), "is_source": o.get("is_source"),
                      "wire": o.get("wire") or 0})
        for k, t in enumerate(hit["right_inside"] or []):
            terms.append({"index": "INSIDE[%d]" % k, "name": t.get("name"),
                          "is_source": t.get("is_source"), "wire": t.get("wire") or 0})
        rec = {"found": True, "reg_index": hit["reg_index"], "class": hit["right_class"],
               "label_read_off_the_machine": o.get("name"), "terminal_count": len(terms),
               "terminals": terms, "partner_left_uid": hit["left_uid"],
               "outer_wire": o.get("wire") or 0}
        out[uid] = rec
        fact("M4 RIGHT #%d (%s, reg_index %d, LEFT partner #%r): LABEL %r ; %d terminal(s)"
             % (uid, rec["class"], rec["reg_index"], rec["partner_left_uid"],
                rec["label_read_off_the_machine"], rec["terminal_count"]))
        for t in terms:
            fact("    M4 #%d %-10s name=%-32r is_source=%-5r wire=%r"
                 % (uid, t["index"], t["name"], t["is_source"], t["wire"]))
        fact("M4 #%d OUTER terminal BARE (wire 0)? %r  - measured, not assumed"
             % (uid, (o.get("wire") or 0) == 0))
    R["M4"]["right_registers"] = out
    dump()


# ============================================================ [6] M5 - addressability
def locate_in_terms(terms, want_name, want_source, want_wire):
    """Which Terminals[] row is this endpoint? A WIRED endpoint is identified by its WIRE UID (unique on
    the diagram). A BARE one has no wire, so every candidate of the right direction and name is listed
    and the answer is reported AMBIGUOUS when there is more than one. Nothing is guessed."""
    if want_wire:
        hits = [t for t in terms if (t.get("wire") or 0) == want_wire]
        return hits, "by WIRE UID %d (unique on the diagram)" % want_wire
    hits = [t for t in terms if t.get("name") == want_name and t.get("is_source") is want_source
            and not (t.get("wire") or 0)]
    return hits, ("BARE, so by (name %r, is_source %r, no wire)" % (want_name, want_source))


def phase_m5(border_terms, hints):
    head("[6] M5 - ADDRESSABILITY as Diagram(idx).Nodes[n].Terminals[t], resolved LIVE by uid")
    fact("M5 CONTEXT, not an assumption carried forward: FlatSequenceInnerTunnels #4194 / #3974 were "
         "established last cycle as NOT Nodes[] members (diag_c73_m3a2_rows.log:65,:80).")
    bidx = (R["M3"].get("border_node") or {}).get("diagram_index")
    bnode = (R["M3"].get("border_node") or {}).get("nodes_index")
    fact("M5 THE LIVE BORDER TERMINAL TABLE of #%d (Diagram idx %r, Nodes[%r]), index by index:"
         % (LOOP_NEW, bidx, bnode))
    for t in border_terms:
        fact("    M5 t%-3d name=%-34r is_source=%-5r wire=%-8r state=%s"
             % (t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)))
    found = []
    # (a) + (b) the two NEW RIGHT registers' OUTER terminals, addressed through the border node
    for uid in NEW_RIGHT:
        rec4 = ((R["M4"].get("right_registers") or {}).get(uid) or {})
        o = next((t for t in (rec4.get("terminals") or []) if t["index"] == "OUTER"), {})
        hits, how = locate_in_terms(border_terms, o.get("name"), o.get("is_source"),
                                    o.get("wire") or 0)
        rec = {"endpoint": "RightShiftRegister #%d OUTER" % uid,
               "diagram_index": bidx, "nodes_index": bnode,
               "terminal_indices": [t["i"] for t in hits],
               "names": [t["name"] for t in hits], "how": how,
               "reachable": len(hits) == 1,
               "ambiguous": len(hits) > 1}
        found.append(rec)
        fact("M5 #%d OUTER -> Diagram(%r).Nodes[%r].Terminals%r  names %r ; %s ; reachable-uniquely %r"
             % (uid, bidx, bnode, rec["terminal_indices"], rec["names"], how, rec["reachable"]))
    # (c) Global #7202 terminal 0 'Focus position'
    loc, gterms = M.node_view(SCRATCH, GLOBAL_UID, hints, "M5 Global #%d" % GLOBAL_UID, quiet=True)
    f = loc.get("found") or {}
    grec = {"endpoint": "Global #%d terminal 0 'Focus position'" % GLOBAL_UID,
            "diagram_index": f.get("diagram_index"), "diagram_uid": f.get("diagram_uid"),
            "nodes_index": f.get("nodes_index"), "uid_echo": loc.get("uid_echo"),
            "label": f.get("label"), "terminal_count": len(gterms),
            "terminals": [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                           "wire": t["wire"]} for t in gterms],
            "diagrams_scanned": len(loc.get("scanned") or [])}
    grec["reachable"] = f.get("nodes_index") is not None
    found.append(grec)
    if grec["reachable"]:
        fact("M5 Global #%d FOUND: Diagram idx %r (uid #%r), Nodes[%r], uid echo %r, label %r, %d "
             "terminal(s)" % (GLOBAL_UID, f.get("diagram_index"), f.get("diagram_uid"),
                              f.get("nodes_index"), loc.get("uid_echo"), f.get("label"), len(gterms)))
        for t in gterms:
            fact("    M5 Global #%d t%-2d name=%-30r is_source=%-5r wire=%r"
                 % (GLOBAL_UID, t["i"], t["name"], t["is_source"], t["wire"]))
    else:
        fact("M5 Global #%d NOT FOUND in any diagram's Nodes[] after %d diagram(s) scanned"
             % (GLOBAL_UID, grec["diagrams_scanned"]))
    # (d) FlatSequenceInnerTunnel #7468 - exhaustive walk
    loc2, fterms = M.node_view(SCRATCH, FSIT_UID, hints, "M5 FSIT #%d" % FSIT_UID, quiet=True)
    f2 = loc2.get("found") or {}
    frec = {"endpoint": "FlatSequenceInnerTunnel #%d" % FSIT_UID,
            "diagram_index": f2.get("diagram_index"), "diagram_uid": f2.get("diagram_uid"),
            "nodes_index": f2.get("nodes_index"), "uid_echo": loc2.get("uid_echo"),
            "terminal_count": len(fterms), "diagrams_scanned": len(loc2.get("scanned") or []),
            "scan_stopped": loc2.get("scan_stopped"),
            "reachable": f2.get("nodes_index") is not None}
    found.append(frec)
    if frec["reachable"]:
        fact("M5 FSIT #%d FOUND: Diagram idx %r (uid #%r), Nodes[%r], uid echo %r, %d terminal(s)"
             % (FSIT_UID, f2.get("diagram_index"), f2.get("diagram_uid"), f2.get("nodes_index"),
                loc2.get("uid_echo"), len(fterms)))
        for t in fterms:
            fact("    M5 FSIT #%d t%-2d name=%-30r is_source=%-5r wire=%r"
                 % (FSIT_UID, t["i"], t["name"], t["is_source"], t["wire"]))
    else:
        fact("M5 FSIT #%d NOT FOUND as a Nodes[] member after an exhaustive walk of %d diagram(s)%s"
             % (FSIT_UID, frec["diagrams_scanned"],
                (" ; scan stopped: " + str(loc2.get("scan_stopped"))) if loc2.get("scan_stopped") else ""))
    R["M5"]["endpoints"] = found
    dump()


# ============================================================ [7] M6 - #7468's owner object
def phase_m6():
    head("[7] M6 - the owner object of FlatSequenceInnerTunnel #%d" % FSIT_UID)
    (cls, ouid), err = safe("M6 owner_of(#%d)" % FSIT_UID, lambda: owner_of(SCRATCH, FSIT_UID),
                            (None, None))
    R["M6"] = {"uid": FSIT_UID, "owner_class": cls, "owner_uid": ouid, "error": err}
    fact("M6 FlatSequenceInnerTunnel #%d is owned by %r #%r%s"
         % (FSIT_UID, cls, ouid, (" ; " + err) if err else ""))
    if ouid:
        (cls2, ouid2), err2 = safe("M6 owner_of(owner #%r)" % ouid, lambda: owner_of(SCRATCH, ouid),
                                   (None, None))
        R["M6"]["owner_owner_class"] = cls2
        R["M6"]["owner_owner_uid"] = ouid2
        fact("M6 and that owner %r #%r is itself owned by %r #%r%s"
             % (cls, ouid, cls2, ouid2, (" ; " + err2) if err2 else ""))
    dump()


# ============================================================================ [8] hygiene tail
def phase_tail():
    head("[8] M8 HYGIENE - references closed, the scratch deleted, the artefact re-hashed")
    safe("[8] close_panel(scratch)", lambda: g.close_panel(SCRATCH))
    safe("[8] g.reset()", g.reset)
    rc, _ = safe("[8] ref_counts()", g.ref_counts, {})
    R["ref_counts"] = rc
    fact("M8 VI Server reference counts: %r" % (rc,))
    live = (rc or {}).get("live", (rc or {}).get("open", None))
    gate("H6 every reference this run opened is closed (live == 0)", live in (0, None), "%r" % (rc,))
    for attempt in range(6):
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
            break
        except Exception as e:                                                     # noqa: BLE001
            fact("M8 scratch delete attempt %d failed: %s" % (attempt + 1, str(e)[:120]))
            time.sleep(4.0)
    still = os.path.exists(SCRATCH)
    R["scratch_still_on_disk"] = still
    gate("H4 the scratch is deleted", not still, "%s" % os.path.basename(SCRATCH))
    pr = probe_hash("H5 THE ARTEFACT AFTER", ARTEFACT)
    gate("H5 the artefact still reads its pinned md5 %s AFTER the run" % ARTEFACT_MD5[:8],
         pr.get("md5") == ARTEFACT_MD5, "%r" % (pr.get("md5"),))
    R["pins_after"] = {}
    allpins = True
    for tag, path, pin in PINS:
        p2 = probe_hash("M8 PIN AFTER %s" % tag, path)
        R["pins_after"][tag] = p2.get("md5")
        allpins = allpins and (p2.get("md5") == pin)
    gate("H2b the four standing pins all hold AFTER the run", allpins, "%r" % (R["pins_after"],))
    R["imported_module_refusals"] = list(getattr(M, "refusals", []))
    fact("M8 machine refusals recorded by the imported helper module: %d %r"
         % (len(R["imported_module_refusals"]), R["imported_module_refusals"][:3]))
    R["handles"]["after"] = labview_handles()
    fact("M8 LabVIEW handles AFTER: %r (before %r, after the restart %r ; baseline ~31,500 - a FACT, "
         "never a gate)" % (R["handles"]["after"], R["handles"].get("before"),
                            R["handles"].get("after_restart")))
    dump()


def main():
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c75_m3a3_endpoints - MEASUREMENT ONLY, hygiene gates only (Pre-decided 63)",
          flush=True)
    print("=== %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=" * 100, flush=True)
    rc = 0
    try:
        phase_0()
        hints = phase_1_scratch()
        phase_m1()
        phase_m2()
        border_terms = phase_m3(hints)
        phase_m4()
        phase_m5(border_terms, hints)
        phase_m6()
    except SystemExit:
        rc = 1
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        tb = traceback.extract_tb(sys.exc_info()[2])
        last = tb[-1] if tb else None
        where = ("%s:%d" % (os.path.basename(last.filename), last.lineno)) if last else "unknown"
        R["our_code_defect"] = {"type": type(e).__name__, "message": str(e)[:400], "raised_at": where}
        # OUR bug, recorded as OURS - never as a machine refusal.
        fact("OUR-CODE DEFECT %s raised at %s: %s" % (type(e).__name__, where, str(e)[:300]))
        gate("the diagnostic ran to the end without a defect in THIS script", False,
             "%s at %s" % (type(e).__name__, where))
        rc = 1
    finally:
        try:
            phase_tail()
        except Exception as e:                                                     # noqa: BLE001
            fact("the hygiene tail itself raised %s: %s" % (type(e).__name__, str(e)[:200]))
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES %d pass / %d fail%s"
          % (len(passes), len(fails), ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("JSON %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 1 if fails else rc


if __name__ == "__main__":
    sys.exit(main())
