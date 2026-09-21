"""diag_c74_m3a2_verify - INDEPENDENT, READ-ONLY verification of the M3a-2 artefact.

WHY THIS EXISTS. `tools/recipes/build_d1_m3a2.py` accepted its two rows against the SOURCE side
(source terminal owner #4194 / #3974, the original sink still on the net, PD85 violations 0). The SINK
side was reported as NODE-TERMINAL addresses - Row A `Nodes[21].Terminals[2]` 'VISA out', Row B
`Nodes[21].Terminals[4]` 'Out position'. Two things about that reading are unconfirmed and both are the
T2c2 failure class (an index addressing something other than what it is believed to address):
  * the indices are EVEN, while the evidence cited for exactly this purpose
    (`tools/bench/build_d1_routeb_v0_run2.log:467-468`) records register terminals INTERLEAVED AT ODD
    indices on this same Diagram #686;
  * Row B's reported terminal name 'Out position' is not the register's own measured name
    'position [internal units]' (`tools/bench/diag_c73_m3a2_rows.log`).
So this file re-asks the question ANCHORED AT THE REGISTER UID and never at a node index: it starts from
the four register uids, reads each one's OUTER terminal through `shift_reg_left` (OpShiftRegs_v1), and
only then asks which row of the border node's `Terminals[]` table that terminal is.

PRIOR ART, CHECKED BEFORE A LINE WAS WRITTEN (CLAUDE.md: check what already exists first).
  * `docs/toolkit-capabilities.md` + `grep '^def ' tools/gscript.py`: the readers this needs all exist -
    `shift_reg_left` :816 (LEFT register uid + its OUTER terminal name/is_source/wire), `node_terms_uid`
    :955 (a node's full terminal table WITH the node's own uid echoed back), `report_all` :502,
    `count` :1035, `exec_state` :2007, `ref_counts` :233.
  * `tools/recipes/build_d1_m3a1.py` already owns the walk/scan helpers - `find_node` :541, `terms_at`
    :500, `term_state` :524, `node_view` :572, `print_walk` :823, `pd85_violations` :811 - and
    `build_opconnectfromwire_v0.wire_source_owner` is the `OpWireSource_v5` reader. They are IMPORTED.
  * NOTHING NEW IS BUILT: no new op VI, no new gscript verb, no new checker, no new device. This file
    only READS, and it never runs the artefact (34(f)).

WHAT IT TOUCHES. A UNIQUE SCRATCH COPY of the artefact, created and deleted in the same run. The
artefact itself is hashed at both ends and never opened. Rig state 조립: no motor, no ASI, no camera.

PREDICTION CONTRACT (the gates; a `FAIL` line means the prediction did not hold)
  H1  the artefact's md5 == 3842f5e6f128226235dc78353f26ef44 BEFORE anything is opened
  H2  the four standing pins (ORIGINAL, S1, S2, THE BED) still read their recorded md5
  H3  the scratch copy starts byte-identical to the artefact
  H4  the scratch is DELETED and is no longer on disk at the end
  H5  the artefact re-reads md5 3842f5e6... AFTER the run (it was never opened)
  H6  every VI Server reference this run opened is closed (ref_counts live == 0)
  V1  LEFT register #23880's OUTER terminal carries a wire, and that wire has EXACTLY ONE source
      terminal OF ANY OWNER CLASS, whose owner uid is #4194  (PD85 violations must be 0 or the walk is
      not believed and V1 FAILS)
  V2  the same for LEFT register #23909, expected source owner #3974
  V3a RIGHT register #23868's OUTER terminal is still BARE (plan item 91 leaves it for M3a-3)
  V3b RIGHT register #23895's OUTER terminal is still BARE
  V4  is a FACT, never a gate: the `Nodes[].Terminals[]` INDEX and NAME each of those four OUTER
      terminals occupies on the live border node, so the odd/even question is answered from the machine.
  Everything else measured here - ExecState, counts, the border node's index - is a FACT line and does
  NOT fail the run (plan item 63).

NOT DECIDED HERE. If V1 or V2 fails, this file reports it and STOPS. It does not repair anything, does
not re-run the build, and does not touch `tools/recipes/build_d1_m3a2.py`.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index                                                 # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")

# ---------------------------------------------------------------- the pins, all read from files
ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi")
ARTEFACT_MD5 = "3842f5e6f128226235dc78353f26ef44"
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C74VERIFY_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c74_m3a2_verify.json")

TOP = 0
D686 = 686                       # the diagram that carries both loop borders and all four wires
LOOP_A = 23032                   # the NEW WhileLoop - M3a-1's registers live on it
REG_PROBE_MAX = 16

# (label, LEFT uid, RIGHT uid, register name as measured by diag_c73, expected source owner, source wire)
ROWS = [
    {"tag": "V1 A VISA", "left_uid": 23880, "right_uid": 23868, "reg_name": "VISA out",
     "source_owner": 4194, "source_wire": 4185, "original_sink": 4344,
     "recipe_claim": "Nodes[21].Terminals[2] 'VISA out'"},
    {"tag": "V2 B POS", "left_uid": 23909, "right_uid": 23895, "reg_name": "position [internal units]",
     "source_owner": 3974, "source_wire": 3968, "original_sink": 4274,
     "recipe_claim": "Nodes[21].Terminals[4] 'Out position'"},
]
ODD_INDEX_EVIDENCE = ("tools/bench/build_d1_routeb_v0_run2.log:467-468 - BARE register terminals on "
                      "Diagram[19] #686 sat at ODD Terminals[] indices (Nodes[22].T[1] 'position "
                      "[internal units]', Nodes[22].T[3] 'VISA out')")

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "artefact": ARTEFACT,
     "artefact_md5_pin": ARTEFACT_MD5, "scratch": SCRATCH,
     "task": "INDEPENDENT READ-ONLY verification of stage M3a-2, anchored at the four REGISTER UIDs and "
             "never at a node index. V1/V2/V3 are gates; V4 is a fact.",
     "verification_level": "STRUCTURAL, never functional (34(f)) - nothing is run",
     "read_only": "the artefact is copied to a unique scratch, the scratch is read and deleted, and the "
                  "artefact's md5 is re-read at the end. The artefact is never opened.",
     "no_new_op": True, "no_new_verb": True, "no_new_device": True, "no_new_checker": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run - the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py is not called",
     "edits_no_recipe": "tools/recipes/build_d1_m3a2.py is neither read for edit nor written",
     "handles": {}, "hash_probe": [], "registers": {}, "rows": {}, "border": {}, "facts_note":
         "find_node / terms_at / node_view / print_walk print through build_d1_m3a1's fact(), so their "
         "lines are in THIS LOG but in that module's in-memory list; its refusals are read at the end."}


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


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


# ============================================================================== [0] files only
def phase_0():
    head("[0] FILES ONLY, ZERO LabVIEW - the md5 pins, then the pre-batch restart")
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500 - a FACT, never a gate)"
         % (R["handles"]["before"],))
    pr = probe_hash("H1 THE ARTEFACT BEFORE", ARTEFACT)
    gate("H1 the artefact reads its pinned md5 %s BEFORE anything is opened" % ARTEFACT_MD5[:8],
         pr.get("md5") == ARTEFACT_MD5, "%r" % (pr.get("md5"),))
    for tag, path, pin in PINS:
        p2 = probe_hash("H2 %s" % tag, path)
        gate("H2 %s md5 == its pin %s" % (tag, pin[:8]), p2.get("md5") == pin, "%r" % (p2.get("md5"),))
    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % (R["handles"]["after_restart"],))
    dump()


# ============================================================================== [1] the scratch
def phase_1_scratch():
    head("[1] THE SCRATCH COPY - the artefact itself is never opened")
    shutil.copy2(ARTEFACT, SCRATCH)
    time.sleep(0.4)
    pr = probe_hash("[1] the scratch straight after the copy", SCRATCH)
    gate("H3 the scratch starts byte-identical to the artefact", pr.get("md5") == ARTEFACT_MD5,
         "%r vs %r" % (pr.get("md5"), ARTEFACT_MD5))
    t0 = time.time()
    _, err = safe("[1] ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("[1] ensure_loaded(scratch) took %.1f s%s" % (time.time() - t0, (" ERROR " + err) if err else ""))
    es, _ = safe("[1] exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state"] = es
    fact("[1] the scratch reads ExecState %r - A FACT ONLY. This artefact is BROKEN BY DESIGN and is "
         "never run (34(f)); nothing here is gated on it or reasoned from it." % (es,))
    cnt = {}
    for c in ("Node", "Wire", "LeftShiftRegister", "RightShiftRegister"):
        cnt[c], _ = safe("[1] count(%r)" % c, lambda cc=c: g.count(SCRATCH, cc))
    R["counts"] = cnt
    fact("[1] narrow class counts on the scratch: %r" % (cnt,))
    di, derr = safe("[1] diag_index(#%d)" % D686, lambda: diag_index(SCRATCH, D686))
    R["d686_index"] = di
    fact("[1] Diagram #%d -> traverse index %r%s" % (D686, di, (" ; " + derr) if derr else ""))
    dump()
    return [di, TOP] if di is not None else [TOP]


# ============================================================ [2] the registers, read BY UID
def reg_table(loop_index, tag, cap=REG_PROBE_MAX):
    """Every shift register of the loop, READ: the RIGHT register's uid/OUTER/INSIDE and the same for its
    LEFT partner. This is the ANCHOR - every later question is asked of a row of this table, never of a
    remembered node-terminal index."""
    out = []
    for k in range(cap):
        sr, err = safe("%s shift_reg_left(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg_left(SCRATCH, loop_index, kk))
        if err or not sr:
            fact("%s reg_index=%d -> READ STOPS HERE: %s" % (tag, k, err or "no row returned"))
            break
        left = sr.get("left") or {}
        row = {"reg_index": k, "right_uid": sr.get("uid"), "right_class": sr.get("class"),
               "right_out": sr.get("out"), "left_uid": left.get("uid"), "left_class": left.get("class"),
               "left_out": left.get("out"), "left_uids": sr.get("left_uids"),
               "op_errors": sr.get("errors")}
        out.append(row)
        fact("%s reg%-2d RIGHT #%-6r %-21r outer=%r | LEFT #%-6r %-21r outer=%r | errors=%r"
             % (tag, k, row["right_uid"], row["right_class"], row["right_out"], row["left_uid"],
                row["left_class"], row["left_out"], row["op_errors"]))
        if row["op_errors"] or row["right_uid"] in (None, 0):
            break
    return out


def phase_2_registers(hints):
    head("[2] THE LOOP AND ITS REGISTERS - read by uid, and the border node's FULL terminal table")
    rows_by_uid = {}
    li_rows, err = safe("[2] report_all('WhileLoop')", lambda: g.report_all(SCRATCH, "WhileLoop"), [])
    idx = next((r["i"] for r in (li_rows or []) if r["uid"] == LOOP_A), None)
    echo = next((r["uid"] for r in (li_rows or []) if r["i"] == idx), None) if idx is not None else None
    fact("[2] A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d ; %d WhileLoop row(s))%s"
         % (idx, echo, LOOP_A, len(li_rows or []), (" ; " + err) if err else ""))
    R["loop_index"] = idx
    R["loop_index_echo"] = echo
    if echo != LOOP_A:
        gate("V0 the loop index for #%d echoes back its own uid" % LOOP_A, False,
             "echo %r - every reading below would be of an unknown loop, so the run stops" % (echo,))
        raise SystemExit(1)
    tbl = reg_table(idx, "[2] loop#%d" % LOOP_A)
    R["registers"]["table"] = tbl
    for r in tbl:
        rows_by_uid[r["right_uid"]] = ("RIGHT", r)
        rows_by_uid[r["left_uid"]] = ("LEFT", r)
    fact("[2] the live register table carries RIGHT uids %r and LEFT uids %r"
         % ([r["right_uid"] for r in tbl], [r["left_uid"] for r in tbl]))

    loc, terms = M.node_view(SCRATCH, LOOP_A, hints, "[2] the loop border #%d" % LOOP_A)
    f = loc.get("found") or {}
    R["border"] = {"diagram_index": f.get("diagram_index"), "diagram_uid": f.get("diagram_uid"),
                   "nodes_index": f.get("nodes_index"), "uid_echo": loc.get("uid_echo"),
                   "terminal_count": len(terms),
                   "terminals": [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                                  "wire": t["wire"], "state": M.term_state(t)} for t in terms]}
    fact("[2] the loop border #%d sits on Diagram idx %r (uid #%r) at Nodes[%r], uid echo %r, with %d "
         "terminal(s). The recipe's rows were reported as Nodes[21]."
         % (LOOP_A, f.get("diagram_index"), f.get("diagram_uid"), f.get("nodes_index"),
            loc.get("uid_echo"), len(terms)))
    dump()
    return rows_by_uid, terms


# ============================================================ [3] V4 - the index, read off the machine
def outer_of(rows_by_uid, uid):
    """The OUTER terminal reading of ONE register uid, taken from the live table (never remembered)."""
    hit = rows_by_uid.get(uid)
    if not hit:
        return None, None
    side, row = hit
    return side, (row["right_out"] if side == "RIGHT" else row["left_out"])


def locate_in_border(terms, outer, side):
    """Which `Terminals[]` row IS this register's OUTER terminal? A WIRED terminal is identified by its
    WIRE UID, which is unique on the diagram - no name matching is needed and none is trusted. A BARE one
    has no wire to match on, so every candidate of the right direction and name is listed and the answer
    is reported as ambiguous when there is more than one. Nothing is guessed (plan item 68)."""
    if not outer:
        return {"rows": [], "how": "the register has no OUTER terminal reading"}
    w = outer.get("wire") or 0
    if w:
        hits = [t for t in terms if (t.get("wire") or 0) == w]
        return {"rows": hits, "how": "by WIRE UID %d (unique on the diagram)" % w}
    want_source = True if side == "RIGHT" else False
    hits = [t for t in terms if t.get("name") == outer.get("name")
            and t.get("is_source") is outer.get("is_source") and not (t.get("wire") or 0)]
    return {"rows": hits, "how": "BARE, so by (name %r, is_source %r, no wire); direction expected %r"
                                % (outer.get("name"), outer.get("is_source"), want_source)}


def phase_3_index_fact(rows_by_uid, terms):
    head("[3] V4 (FACT, NOT A GATE) - the Terminals[] index and NAME of each register's OUTER terminal")
    fact("[3] EXPECTATION being tested, from the previously-cited evidence: %s" % ODD_INDEX_EVIDENCE)
    fact("[3] THE FULL BORDER TERMINAL TABLE, index by index:")
    for t in terms:
        fact("    [3] t%-3d name=%-34r is_source=%-5r wire=%-8r state=%s"
             % (t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)))
    out = []
    for uid in (23880, 23909, 23868, 23895):
        side, outer = outer_of(rows_by_uid, uid)
        loc = locate_in_border(terms, outer, side)
        idxs = [t["i"] for t in loc["rows"]]
        rec = {"register_uid": uid, "side": side, "outer_reading": outer,
               "terminal_indices": idxs, "how": loc["how"],
               "names": [t["name"] for t in loc["rows"]],
               "parities": ["odd" if isinstance(i, int) and i % 2 else "even" for i in idxs]}
        out.append(rec)
        fact("[3] V4 register #%d (%s side): OUTER reads name=%r is_source=%r wire=%r -> border "
             "Terminals index(es) %r, name(s) %r, parity %r ; resolved %s"
             % (uid, side, (outer or {}).get("name"), (outer or {}).get("is_source"),
                (outer or {}).get("wire"), idxs, rec["names"], rec["parities"], loc["how"]))
    R["v4_index_fact"] = out
    for row in ROWS:
        rec = next((r for r in out if r["register_uid"] == row["left_uid"]), None)
        fact("[3] V4 vs THE RECIPE'S CLAIM for %s: the recipe reported %s ; measured here, anchored at "
             "register #%d, the OUTER terminal is at index(es) %r with name(s) %r"
             % (row["tag"], row["recipe_claim"], row["left_uid"],
                (rec or {}).get("terminal_indices"), (rec or {}).get("names")))
    dump()
    return out


# ============================================================ [4] V1 / V2 - the wire and its one source
def wire_walk(tag, wire_uid):
    walk, err = safe("%s OpWireSource_v5(UID 2 = %r)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(SCRATCH, int(wire_uid)) if wire_uid else [], [])
    real = [t for t in (walk or []) if t.get("owner_uid")]
    fact("%s OpWireSource_v5(UID 2 = %r): %d row(s), %d with a REAL owner%s"
         % (tag, wire_uid, len(walk or []), len(real), (" ; " + err) if err else ""))
    for t in (walk or []):
        fact("    %s   t%-2r is_source=%-5r owner_class=%-26r owner_uid=%-7r recip=%r%s"
             % (tag, t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"),
                t.get("recip"), ("  READ ERROR " + str(t["err"])) if t.get("err") else ""))
    bad = M.pd85_violations(wire_uid, walk)
    fact("%s PD85 PRECONDITION (plan item 85): %d real-owner row(s), %d violate recip==queried_uid%s"
         % (tag, len(real), len(bad),
            (" -> %r - THIS WALK IS NOT BELIEVED" % [(t.get("i"), t.get("owner_uid"), t.get("recip"))
                                                     for t in bad]) if bad else ""))
    return walk or [], bad, err


def phase_4_rows(rows_by_uid):
    head("[4] V1 / V2 - each LEFT register's OUTER wire and the ONE source terminal on it")
    for row in ROWS:
        tag = row["tag"]
        side, outer = outer_of(rows_by_uid, row["left_uid"])
        rec = {"tag": tag, "left_uid": row["left_uid"], "side": side, "outer_reading": outer,
               "expected_source_owner": row["source_owner"]}
        fact("%s LEFT register #%d OUTER terminal reads name=%r is_source=%r wire=%r"
             % (tag, row["left_uid"], (outer or {}).get("name"), (outer or {}).get("is_source"),
                (outer or {}).get("wire")))
        if side != "LEFT":
            gate("%s LEFT register #%d is in the live register table" % (tag, row["left_uid"]), False,
                 "the uid resolves to side %r, so no OUTER terminal can be read for it" % (side,))
            R["rows"][tag] = rec
            continue
        w = (outer or {}).get("wire") or 0
        rec["wire"] = w
        if not w:
            gate("%s the LEFT register's OUTER terminal carries a wire" % tag, False,
                 "wire %r - the terminal is BARE, so stage M3a-2's row did not land on this register" % (w,))
            R["rows"][tag] = rec
            dump()
            continue
        gate("%s the LEFT register #%d OUTER terminal carries a wire" % (tag, row["left_uid"]), True,
             "wire %d" % w)
        walk, bad, err = wire_walk("%s the OUTER net" % tag, w)
        srcs = [t for t in walk if t.get("is_source") and t.get("owner_uid")]
        owners = [int(t["owner_uid"]) for t in walk if t.get("owner_uid")]
        rec["walk_error"] = err
        rec["pd85_violations"] = len(bad)
        rec["all_source_terminals"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid"))
                                       for t in srcs]
        rec["every_owner_on_the_net"] = sorted(set(owners))
        rec["original_sink_still_on_the_net"] = row["original_sink"] in owners
        one = srcs[0] if len(srcs) == 1 else None
        rec["the_one_source_owner"] = (one or {}).get("owner_uid")
        rec["owner_matches"] = bool(one is not None and one.get("owner_uid") == row["source_owner"])
        fact("%s the OUTER net (wire %d): %d source terminal(s) OF ANY CLASS %r ; every owner on the net "
             "%r ; the ORIGINAL sink #%d still on it? %r"
             % (tag, w, len(srcs), rec["all_source_terminals"], rec["every_owner_on_the_net"],
                row["original_sink"], rec["original_sink_still_on_the_net"]))
        ok = (not bad) and len(srcs) == 1 and rec["owner_matches"]
        gate("%s the OUTER wire has EXACTLY ONE source terminal of any owner class and its owner is #%d"
             % (tag, row["source_owner"]), ok,
             "sources %d %r ; the one owner %r ; PD85 violations %d (a non-zero count means the walk is "
             "not believed and this gate FAILS rather than drops the row)"
             % (len(srcs), rec["all_source_terminals"], rec["the_one_source_owner"], len(bad)))
        fact("%s SOURCE-WIRE CROSS-CHECK (a fact, not a gate): stage M3a-2 branched wire %d, whose source "
             "was #%d. The wire now on this register's OUTER terminal is %d - the SAME wire uid? %r"
             % (tag, row["source_wire"], row["source_owner"], w, w == row["source_wire"]))
        R["rows"][tag] = rec
        dump()


# ============================================================ [5] V3 - the right registers stay bare
def phase_5_right_bare(rows_by_uid, terms):
    head("[5] V3 - the two RIGHT registers' OUTER terminals must still be BARE (plan item 91, M3a-3)")
    for uid, label in ((23868, "V3a"), (23895, "V3b")):
        side, outer = outer_of(rows_by_uid, uid)
        loc = locate_in_border(terms, outer, side)
        states = [M.term_state(t) for t in loc["rows"]]
        w = (outer or {}).get("wire") or 0
        rec = {"register_uid": uid, "side": side, "outer_reading": outer,
               "terminal_indices": [t["i"] for t in loc["rows"]], "border_states": states}
        R["registers"].setdefault("right_bare", []).append(rec)
        fact("%s RIGHT register #%d OUTER reads name=%r is_source=%r wire=%r ; border row(s) %r state(s) "
             "%r (%s)" % (label, uid, (outer or {}).get("name"), (outer or {}).get("is_source"), w,
                          rec["terminal_indices"], states, loc["how"]))
        gate("%s RIGHT register #%d's OUTER terminal is still BARE" % (label, uid), side == "RIGHT" and w == 0,
             "side %r, wire %r - anything other than 0 means something was wired that this stage was not "
             "meant to wire" % (side, w))
    dump()


# ============================================================================== [6] hygiene tail
def phase_6_tail():
    head("[6] HYGIENE - references closed, the scratch deleted, the artefact re-hashed")
    safe("[6] g.reset()", g.reset)
    rc, _ = safe("[6] ref_counts()", g.ref_counts, {})
    R["ref_counts"] = rc
    fact("[6] VI Server reference counts: %r" % (rc,))
    live = (rc or {}).get("live", (rc or {}).get("open", None))
    gate("H6 every reference this run opened is closed (live == 0)", live in (0, None),
         "%r" % (rc,))
    try:
        os.remove(SCRATCH)
    except Exception as e:                                                         # noqa: BLE001
        fact("[6] removing the scratch raised %s: %s" % (type(e).__name__, str(e)[:200]))
    still = os.path.exists(SCRATCH)
    R["scratch_still_on_disk"] = still
    gate("H4 the scratch is deleted", not still, "%s" % os.path.basename(SCRATCH))
    pr = probe_hash("H5 THE ARTEFACT AFTER", ARTEFACT)
    gate("H5 the artefact still reads its pinned md5 %s AFTER the run" % ARTEFACT_MD5[:8],
         pr.get("md5") == ARTEFACT_MD5, "%r" % (pr.get("md5"),))
    R["imported_module_refusals"] = list(getattr(M, "refusals", []))
    fact("[6] machine refusals recorded by the imported helper module: %d %r"
         % (len(R["imported_module_refusals"]), R["imported_module_refusals"][:3]))
    R["handles"]["after"] = labview_handles()
    fact("[6] LabVIEW handles AFTER: %r (before %r, after the restart %r ; baseline ~31,500 - a FACT, "
         "never a gate)" % (R["handles"]["after"], R["handles"].get("before"),
                            R["handles"].get("after_restart")))
    dump()


def main():
    print("=== diag_c74_m3a2_verify  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== READ-ONLY verification of %s" % os.path.basename(ARTEFACT), flush=True)
    rc = 0
    try:
        phase_0()
        hints = phase_1_scratch()
        rows_by_uid, terms = phase_2_registers(hints)
        phase_3_index_fact(rows_by_uid, terms)
        phase_4_rows(rows_by_uid)
        phase_5_right_bare(rows_by_uid, terms)
    except SystemExit:
        rc = 1
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        tb = traceback.extract_tb(sys.exc_info()[2])
        last = tb[-1] if tb else None
        where = ("%s:%d" % (os.path.basename(last.filename), last.lineno)) if last else "unknown"
        R["our_code_defect"] = {"type": type(e).__name__, "message": str(e)[:400], "raised_at": where}
        # OUR bug, recorded as OURS - never as a machine refusal (the mislabel repaired this cycle).
        fact("OUR-CODE DEFECT %s raised at %s: %s" % (type(e).__name__, where, str(e)[:300]))
        gate("the verification ran to the end without a defect in THIS script", False,
             "%s at %s" % (type(e).__name__, where))
        rc = 1
    finally:
        try:
            phase_6_tail()
        except Exception as e:                                                     # noqa: BLE001
            fact("the hygiene tail itself raised %s: %s" % (type(e).__name__, str(e)[:200]))
        dump()
    print("\n=== GATES %d pass / %d fail%s"
          % (len(passes), len(fails), ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== JSON %s" % OUT, flush=True)
    return 1 if fails else rc


if __name__ == "__main__":
    sys.exit(main())
