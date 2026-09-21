"""DIAGNOSTIC, MEASUREMENT ONLY - the M3a-3 evidence table (the two downstream consumers).

WHAT THIS IS NOT: it builds nothing, it creates no op, it edits no deliverable, it runs no VI. It
COPIES the M3a-2 artefact to a unique scratch name, READS the scratch, deletes the scratch, and
re-reads the artefact's md5 to prove it is byte-unchanged. Per `docs/cycle27-plan.md` Pre-decided 63
a measurement-only diagnostic GATES ON HYGIENE ONLY: a negative measurement is a FACT line, never a
failing gate. `ExecState` is recorded once as a FACT and is NEVER read as a discriminator (the
artefact is BROKEN BY DESIGN; Pre-decided 95, 42(c)).

PRIOR ART CHECKED BEFORE WRITING A LINE (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/diag_c73_m3a2_rows.py` - the verified pattern this file is cut from (hygiene gates
    H1-H5, uid-echo discipline, reg_table, wire_walk, the deadline reserve). Its run:
    `tools/bench/diag_c73_m3a2_rows.log`, 143 s, rc=0.
  * `tools/bench/diag_c62_branch.py:532-588` - the TERMINAL-SIDE REVERSE CENSUS (node_terms_uid over
    every node of one diagram + panel_wiring rows), the method M3 below is required to use.
  * `tools/gscript.py` - `shift_reg_left` :816, `node_terms_uid` :955, `node_labels` :601,
    `panel_wiring` :856, `tunnels` :971 (LoopTunnel ONLY - shift registers are not LoopTunnels),
    `report_all` :502, `exec_state` :2007, `ensure_loaded` :1298, `ref_counts` :233.
  * `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` (OpWireSource_v5) - the
    WIRE-SIDE reader, REPAIRED 2026-09-22. Used here ONLY as a labelled SECONDARY cross-check; the
    brief forbids trusting it for the net question.
  * `tools/recipes/build_d1_v0.py` - `owner_of` :338 (strict uid echo) and `diag_index` :357.
  * `tools/recipes/build_d1_m3a1.py` - `find_node` :541, `terms_at` :500, `term_state` :524 (imported).
NOTHING NEW IS BUILT (user, 2026-09-18 08:53 "장치는 더 만들지 말고 계속 진행").

PREDICTION CONTRACT (the hygiene gates; these are the ONLY things that can FAIL):
  H1  the artefact's md5 is `3842f5e6f128226235dc78353f26ef44` BEFORE the run.
  H2  the artefact's md5 is unchanged AFTER the run.
  H3  the four STATUS md5 pins (ORIGINAL, S1, S2, THE BED) all hold after the run.
  H4  the scratch copy is deleted and no longer on disk.
  H5  gscript's in-process VI-Server reference counter is level (opened == closed) at exit.
  H6  every `OpWireSource_v5` row on every walk satisfies `recip == queried_uid` (Pre-decided 85).
MEASUREMENT EXPECTATIONS (recorded, NOT gated - a mismatch is a FACT, never a failure):
  E1  loop #637 carries 15 register slots; slot 1 = #4256/#4274, slot 2 = #4334/#4344
      (`diag_c73_m3a2_rows.log:43-44`, byte-identical bed).
  E2  loop #23032 carries 2; reg0 #23868/#23880 'VISA out', reg1 #23895/#23909 'position ...'.
  E3  both RIGHT OUTER terminals on #23032 are still BARE (wire 0).
  E4  wire 4859 reaches `Global #7202` t0 'Focus position'; wire 7506 reaches
      `FlatSequenceInnerTunnel #7468`.
  E5  #637, #23032, 4859 and 7506 are all owned by Diagram #686.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if p not in sys.path:
        sys.path.insert(0, p)

import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles, restart_labview                           # noqa: E402
from build_d1_v0 import diag_index, owner_of                                      # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS            # noqa: E402
from build_d1_m3a1 import find_node, terms_at, term_state                         # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

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
OUT = os.path.join(BENCH, "diag_c75_m3a3_rows.json")

LOOP_OLD = 637                     # the ORIGINAL While loop
LOOP_NEW = 23032                   # the NEW While loop (M3a-1/M3a-2's registers live on it)
D686 = 686                         # the diagram said to own both loops and both wires - MEASURED
OLD_LEFTS = {"VISA (fed by wire 4185)": 4344, "position (fed by wire 3968)": 4274}
OLD_RIGHT_CANDIDATES = (4256, 4334)
NEW_REGS = {"reg0 VISA": {"right": 23868, "left": 23880},
            "reg1 position": {"right": 23895, "left": 23909}}
NET_WIRES = (4859, 7506)
CONSUMERS = {4859: ("Global", 7202, "Focus position"),
             7506: ("FlatSequenceInnerTunnel", 7468, "")}
M4_OBJECTS = [("Global consumer", 7202), ("FlatSequenceInnerTunnel consumer", 7468),
              ("WhileLoop OLD", LOOP_OLD), ("WhileLoop NEW", LOOP_NEW),
              ("wire 4859", 4859), ("wire 7506", 7506)]
REG_PROBE_MAX = 17
NODE_CENSUS_CAP = 260
TUNNEL_CAP = 160
RUN_DEADLINE_S = 20 * 60.0
RESERVE_S = 150.0

T0 = time.time()
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "scratch": SCRATCH,
     "artefact": ARTEFACT, "M1": {}, "M2": {}, "M3": {}, "M4": {}, "M5": {}, "M6": {},
     "hash_probe": [], "pd85_violation_total": 0}
passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(t):
    print("\n---------- %s" % t, flush=True)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                        # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


# ------------------------------------------------------------------ readers, all uid-ECHOED
def loop_index_of(uid, tag):
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(SCRATCH, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d ; %d WhileLoop row(s))"
         % (tag, idx, echo, uid, len(rows or [])))
    return idx if echo == uid else None


def reg_table(loop_index, tag, cap=REG_PROBE_MAX):
    """Every shift-register SLOT of one loop: the RIGHT register and its LEFT partner, each with its
    OUTER terminal and its INSIDE terminals (OpShiftRegs_v1 via gscript.shift_reg_left:816). A shift
    register is NOT a Diagram.Nodes[] member, so there is no Terminals[] index for it: the OUTER
    terminal is the `Outside Terminal` property and the inside ones are `Inside Terminals[k]`. That
    addressing fact is printed once by the caller and never guessed at."""
    out = []
    for k in range(cap):
        if left_s() < 45:
            fact("%s reg slot %d: deadline reserve reached, table incomplete (reported, not guessed)"
                 % (tag, k))
            break
        sr, err = safe("%s shift_reg_left(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg_left(SCRATCH, loop_index, kk))
        if err or not sr:
            fact("%s reg slot %d -> READ ERROR %s" % (tag, k, err))
            break
        row = {"slot": k, "right_uid": sr.get("uid"), "right_class": sr.get("class"),
               "right_out": sr.get("out"), "right_inside": sr.get("inside"),
               "left_uids": sr.get("left_uids"), "left_uid": (sr.get("left") or {}).get("uid"),
               "left_class": (sr.get("left") or {}).get("class"),
               "left_out": (sr.get("left") or {}).get("out"),
               "left_inside": (sr.get("left") or {}).get("inside"),
               "op_errors": sr.get("errors")}
        out.append(row)
        if row["op_errors"]:
            fact("%s reg slot %d -> op errors %r (past the end of Shift Registers[]); table ends here"
                 % (tag, k, row["op_errors"]))
            break
        fact("%s slot %d RIGHT #%r %r outer=%r inside=%r | LEFT #%r %r outer=%r inside=%r"
             % (tag, k, row["right_uid"], row["right_class"], row["right_out"], row["right_inside"],
                row["left_uid"], row["left_class"], row["left_out"], row["left_inside"]))
        if row["right_uid"] in (None, 0):
            break
    return out


def flatten_regs(tbl, tag):
    """Every terminal of every register in a reg_table, one FACT line each, BARE marked."""
    flat = []
    for r in tbl:
        if r.get("op_errors"):
            continue
        for side, uid, cls, o, ins in (("RIGHT", r["right_uid"], r["right_class"], r["right_out"],
                                        r["right_inside"]),
                                       ("LEFT", r["left_uid"], r["left_class"], r["left_out"],
                                        r["left_inside"])):
            if o is not None:
                flat.append({"slot": r["slot"], "side": side, "uid": uid, "class": cls,
                             "terminal": "OUTER (Outside Terminal property)", "name": o.get("name"),
                             "is_source": o.get("is_source"), "wire": o.get("wire") or 0})
            for k, t in enumerate(ins or []):
                flat.append({"slot": r["slot"], "side": side, "uid": uid, "class": cls,
                             "terminal": "INSIDE[%d]" % k, "name": t.get("name"),
                             "is_source": t.get("is_source"), "wire": t.get("wire") or 0})
    for t in flat:
        fact("%s TERM slot%d %-5s #%-7r %-19s %-32s name=%-30r is_source=%-5r wire=%s"
             % (tag, t["slot"], t["side"], t["uid"], t["class"], t["terminal"], t["name"],
                t["is_source"], (t["wire"] if t["wire"] else "0 = BARE")))
    return flat


def wire_walk(wire_uid, tag, n=10):
    """SECONDARY, labelled: every terminal the WIRE-SIDE reader (OpWireSource_v5) reports for one wire.
    Pre-decided 85 is asserted per row: a real-owner row must echo `recip == the queried wire uid`."""
    rec = {"wire": wire_uid, "rows": [], "pd85_violations": [], "error": "", "reader": "WIRE-SIDE"}
    if not wire_uid:
        fact("%s wire 0 - the terminal is BARE, there is no wire to walk" % tag)
        return rec
    rows, err = safe("%s wire_source_owner(%r)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(SCRATCH, wire_uid, n=n), [])
    rec["error"] = err
    real = 0
    for r in (rows or []):
        rec["rows"].append(r)
        if r.get("owner_uid"):
            real += 1
            bad = (r.get("recip") != wire_uid)
            if bad:
                rec["pd85_violations"].append(r)
            fact("    %s w%-7r t%-2d is_source=%-5r owner_class=%-24r owner_uid=%-7r recip=%r%s"
                 % (tag, wire_uid, r["i"], r.get("is_source"), r.get("owner_class"),
                    r.get("owner_uid"), r.get("recip"), ("  PD85 VIOLATION" if bad else "")))
        else:
            fact("    %s w%-7r t%-2d NO OWNER  %r"
                 % (tag, wire_uid, r["i"], (r.get("err") or "")[:110]))
    rec["real_owner_rows"] = real
    R["pd85_violation_total"] += len(rec["pd85_violations"])
    fact("%s wire %r WIRE-SIDE: %d row(s), %d with a REAL owner, %d PD85 violation(s)"
         % (tag, wire_uid, len(rows or []), real, len(rec["pd85_violations"])))
    return rec


# ================================================================== [0] files only, zero LabVIEW
def phase_0():
    head("[0] FILES ONLY - the artefact's md5 BEFORE anything, and the four pins")
    got = md5(ARTEFACT)
    R["artefact_md5_before"] = got
    R["artefact_bytes"] = os.path.getsize(ARTEFACT)
    gate("H1 artefact md5 before == %s" % ARTEFACT_MD5, got == ARTEFACT_MD5,
         "got %s, %d bytes" % (got, R["artefact_bytes"]))
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    line = HASH(ARTEFACT)
    R["hash_probe"].append({"tag": "artefact", "line": line})
    fact("hash_probe artefact: %s" % line)


# ================================================================== [M5] pure text, zero LabVIEW
M5_ROWS = [
    ("connect_from_wire / OpConnectFromWire_v0",
     "tools/recipes/build_opconnectfromwire_v0.py:381-420",
     "SOURCE = (WIRE uid, terminal index ON THAT WIRE); SINK = (sink_diag, sink_node, sink_term) "
     "= Diagram[].Nodes[].Terminals[]",
     "NO - the source is addressed THROUGH a wire object (`labels['wire_uid']` :391), so a BARE "
     "terminal carrying no wire cannot be named at all",
     "NO - it needs a wire uid, and a bare RIGHT-register OUTER has wire 0"),
    ("connect_terminals / OpConnect_v0 (gscript)",
     "tools/gscript.py:2518-2542",
     "SOURCE = (src_node, src_term) and SINK = (sink_node, sink_term), both Nodes[] indices on "
     "DIAGRAM 0 only (no diagram argument)",
     "YES - an unwired source terminal is legal; docstring warns only that an already-wired SINK "
     "is unsafe",
     "NO - a shift register is not a Diagram.Nodes[] member, so no src_node index names it"),
    ("connect_nested_v1 / OpConnectNested_v1",
     "tools/recipes/build_opconnectnested_v1.py:418-453",
     "SOURCE = (src_diag, src_node, src_term); SINK = (sink_diag, sink_node, sink_term) - both "
     "ends Diagram[].Nodes[].Terminals[]",
     "YES - nothing in the wrapper requires the source to carry a wire",
     "NO - same reason: Nodes[]-indexed at both ends"),
    ("connect_nested_v2 / connect2 (gscript)",
     "tools/gscript.py:2965-2999 and :2744-2766",
     "same (diagram index, node index, terminal index) pair as v1; v2 reads no UID/Name/Is Broken? "
     "properties",
     "YES",
     "NO - Nodes[]-indexed at both ends"),
    ("wire_sr / OpWireSR_<variant>_v0",
     "tools/gscript.py:737-776 + tools/bench/opwiresr_labels.json (4 variants ONLY)",
     "register side chosen by VARIANT: 'LeftIn' (left INSIDE -> body node term), 'RightIn' (body "
     "node term -> right INSIDE), 'LeftOutNode' (top-level node term -> LEFT OUTER), 'LeftOutCtl' "
     "(Panel.Controls[ctl] -> LEFT OUTER); loop by (class_name, loop_index), register by reg_index, "
     "the other end by (node_index, term_index) or ctl_index",
     "YES for the node end (Terminal.Connect Wire is invoked on the SINK)",
     "NO - THERE IS NO 'RightOut' VARIANT. The four `OpWireSR_*_v0.vi` on disk are LeftIn, RightIn, "
     "LeftOutNode, LeftOutCtl (Glob of claudeDev, 2026-09-22); the RIGHT register's OUTER terminal "
     "is a SOURCE and no variant takes it"),
    ("wire_indicators / OpWireInd_v0",
     "tools/gscript.py:1786-1828",
     "SOURCE = (node_index, src_terms BY NAME) on `diagram_index`, node_class default 'SubVI'; "
     "SINK = existing front-panel indicators BY LABEL",
     "NO - explicitly: 'Each source terminal MUST ALREADY BE WIRED ... an UNWIRED source makes it "
     "extend an unrelated wire' (:1795-1799)",
     "NO - node-indexed source, and the sink can only be a front-panel indicator"),
    ("move_in / OpMoveIn (build_d1_v0)",
     "tools/recipes/build_d1_v0.py:318-335",
     "NOT A WIRE VERB - it moves the object with `uid` into `dest_diagram_index` at `position` "
     "(GObject.Move with an owner). Creates no wire.",
     "n/a",
     "n/a - it creates no wire"),
    ("delete_object / OpDelete_v0",
     "tools/gscript.py:2348-2401",
     "NOT A WIRE VERB - deletes the `index`-th object of Traverse class `cls`. 'Wires attached to "
     "the object are left broken'. `Wire` IS a Traverse class, so a WIRE can be deleted by its "
     "census index (the shape `delete_by_uid`, build_d1_m3a1.py:583, uses).",
     "n/a",
     "n/a - it creates no wire"),
]


def phase_m5():
    head("[M5] VERB CAPABILITY CENSUS - read-only, no LabVIEW, every row cited to file:line")
    R["M5"]["rows"] = []
    for name, cite, addressing, bare_src, sr_outer in M5_ROWS:
        R["M5"]["rows"].append({"verb": name, "cite": cite, "addressing": addressing,
                                "source_may_be_bare": bare_src,
                                "can_address_a_shift_register_OUTER_as_SOURCE": sr_outer})
        fact("M5 %s  [%s]" % (name, cite))
        fact("M5     addressing: %s" % addressing)
        fact("M5     may its SOURCE be a BARE terminal? %s" % bare_src)
        fact("M5     can it address a shift-register OUTER as SOURCE? %s" % sr_outer)
    R["M5"]["verdict"] = (
        "NO verb in tools/gscript.py or tools/recipes/ addresses a shift-register OUTER terminal as a "
        "SOURCE: the (diagram, node, terminal) family cannot name a non-Nodes[] object, wire_sr has no "
        "RightOut variant, and OpConnectFromWire_v0 needs a WIRE on the source side - which a bare "
        "RIGHT OUTER does not have.")
    fact("M5 VERDICT: %s" % R["M5"]["verdict"])


# ================================================================== [1] restart + the scratch copy
def phase_1():
    head("[1] RESTART LabVIEW (STATUS: left running at 42,297 handles), then the scratch copy")
    before, _ = safe("handles before restart", labview_handles)
    R["M6"]["handles_before_restart"] = before
    fact("M6 LabVIEW handle count BEFORE the restart: %r (baseline ~31,500)" % before)
    _, err = safe("restart_labview", restart_labview)
    R["M6"]["restart_error"] = err
    g.reset()
    time.sleep(3.0)
    after, _ = safe("handles after restart", labview_handles)
    R["M6"]["handles_after_restart"] = after
    fact("M6 LabVIEW handle count AFTER the restart: %r (baseline ~31,500)" % after)
    shutil.copyfile(ARTEFACT, SCRATCH)
    time.sleep(0.4)
    R["scratch_md5"] = md5(SCRATCH)
    fact("scratch %s md5 %s (copy of the artefact, %d bytes)"
         % (os.path.basename(SCRATCH), R["scratch_md5"], os.path.getsize(SCRATCH)))
    t = time.time()
    _, err = safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("ensure_loaded(scratch) took %.1f s%s"
         % (time.time() - t, ((" ERROR " + err) if err else "")))
    es, _ = safe("exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state_cold"] = es
    fact("ExecState of the scratch (= the artefact) = %r - RECORDED ONLY; the artefact is broken BY "
         "DESIGN and ExecState is NEVER a discriminator here (Pre-decided 95, 42(c))" % es)


# ================================================================== [M1] the OLD loop's pairing
def phase_m1():
    head("[M1] THE PAIRING - every shift-register slot of the OLD loop #637")
    li = loop_index_of(LOOP_OLD, "M1")
    R["M1"]["loop_index"] = li
    if li is None:
        fact("M1 loop #%d NOT RESOLVED - M1 cannot be read" % LOOP_OLD)
        return
    fact("M1 ADDRESSING FACT: a shift register is not a Diagram.Nodes[] member, so it has no "
         "Terminals[] index. OpShiftRegs_v1 exposes exactly two terminal kinds per register: the "
         "OUTER one (the `Outside Terminal` property) and `Inside Terminals[k]`, printed below as "
         "INSIDE[k]. No index is carried from any census (Pre-decided 99 A4).")
    tbl = reg_table(li, "M1 loop#637")
    R["M1"]["registers"] = tbl
    real = [r for r in tbl if not r.get("op_errors")]
    fact("M1 loop #637 carries %d readable register slot(s); RIGHT uids %r ; LEFT uids %r"
         % (len(real), [r["right_uid"] for r in real], [r["left_uid"] for r in real]))
    R["M1"]["terminals"] = flatten_regs(tbl, "M1")
    R["M1"]["pairing"] = {}
    for label, left_uid in OLD_LEFTS.items():
        hit = next((r for r in real if r["left_uid"] == left_uid), None)
        if hit is None:
            R["M1"]["pairing"][label] = {"left_uid": left_uid, "found": False}
            fact("M1 PAIRING %s: LEFT #%d is NOT in the live register table - measured absent"
                 % (label, left_uid))
            continue
        rec = {"left_uid": left_uid, "found": True, "slot": hit["slot"],
               "right_uid": hit["right_uid"], "right_class": hit["right_class"],
               "right_outer": hit["right_out"], "left_outer": hit["left_out"],
               "right_is_one_of_the_two_candidates": hit["right_uid"] in OLD_RIGHT_CANDIDATES}
        R["M1"]["pairing"][label] = rec
        fact("M1 PAIRING %s: LEFT #%d sits in register SLOT %d, and the RIGHT register in that SAME "
             "slot is #%r (class %r)" % (label, left_uid, hit["slot"], hit["right_uid"],
                                         hit["right_class"]))
        fact("M1 PAIRING %s: that RIGHT register's OUTER terminal is name=%r is_source=%r wire=%r ; "
             "the LEFT's OUTER is name=%r is_source=%r wire=%r"
             % (label, (hit["right_out"] or {}).get("name"), (hit["right_out"] or {}).get("is_source"),
                (hit["right_out"] or {}).get("wire"), (hit["left_out"] or {}).get("name"),
                (hit["left_out"] or {}).get("is_source"), (hit["left_out"] or {}).get("wire")))
    for cand in OLD_RIGHT_CANDIDATES:
        hit = next((r for r in real if r["right_uid"] == cand), None)
        if hit is None:
            fact("M1 RIGHT #%d is NOT in the live register table - measured absent" % cand)
            continue
        fact("M1 RIGHT #%d: slot %d, partner LEFT #%r, OUTER wire %r, INSIDE %r"
             % (cand, hit["slot"], hit["left_uid"], (hit["right_out"] or {}).get("wire"),
                [(t.get("name"), t.get("wire")) for t in (hit["right_inside"] or [])]))


# ================================================================== [M2] the NEW loop's sources
def phase_m2():
    head("[M2] THE NEW SOURCES - every terminal of the two registers on loop #23032")
    li = loop_index_of(LOOP_NEW, "M2")
    R["M2"]["loop_index"] = li
    if li is None:
        fact("M2 loop #%d NOT RESOLVED - M2 cannot be read" % LOOP_NEW)
        return
    tbl = reg_table(li, "M2 loop#23032", cap=5)
    R["M2"]["registers"] = tbl
    real = [r for r in tbl if not r.get("op_errors")]
    fact("M2 loop #23032 carries %d readable register slot(s); RIGHT uids %r ; LEFT uids %r"
         % (len(real), [r["right_uid"] for r in real], [r["left_uid"] for r in real]))
    R["M2"]["terminals"] = flatten_regs(tbl, "M2")
    R["M2"]["outer_state"] = {}
    for label, want in NEW_REGS.items():
        hit = next((r for r in real if r["right_uid"] == want["right"]), None)
        if hit is None:
            R["M2"]["outer_state"][label] = {"found": False}
            fact("M2 %s: RIGHT #%d NOT in the live table - measured absent" % (label, want["right"]))
            continue
        ro = hit["right_out"] or {}
        lo = hit["left_out"] or {}
        rec = {"found": True, "slot": hit["slot"], "right_uid": hit["right_uid"],
               "left_uid": hit["left_uid"], "left_uid_matches_plan": (hit["left_uid"] == want["left"]),
               "right_outer_name": ro.get("name"), "right_outer_is_source": ro.get("is_source"),
               "right_outer_wire": ro.get("wire") or 0,
               "right_outer_bare": not bool(ro.get("wire")),
               "left_outer_wire": lo.get("wire") or 0,
               "right_inside": hit["right_inside"], "left_inside": hit["left_inside"]}
        R["M2"]["outer_state"][label] = rec
        fact("M2 %s: slot %d ; RIGHT #%r ; LEFT #%r (plan says #%d, equal %r)"
             % (label, hit["slot"], hit["right_uid"], hit["left_uid"], want["left"],
                rec["left_uid_matches_plan"]))
        fact("M2 %s THE OUTER TERMINAL of RIGHT #%r is the `Outside Terminal` property (there is NO "
             "Terminals[] index for a shift register): name=%r is_source=%r wire=%r -> %s"
             % (label, hit["right_uid"], ro.get("name"), ro.get("is_source"), ro.get("wire") or 0,
                ("STILL BARE" if rec["right_outer_bare"] else "WIRED")))
        fact("M2 %s LEFT #%r OUTER: wire %r (M3a-2's initial-value row) ; RIGHT INSIDE %r ; LEFT "
             "INSIDE %r" % (label, hit["left_uid"], lo.get("wire") or 0,
                            [(t.get("name"), t.get("wire")) for t in (hit["right_inside"] or [])],
                            [(t.get("name"), t.get("wire")) for t in (hit["left_inside"] or [])]))


# ================================================================== [M4] diagram ownership
def phase_m4():
    head("[M4] DIAGRAM OWNERSHIP - owner_of under STRICT uid echo, plus the live Nodes[] index")
    diags, _ = safe("M4 report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    R["M4"]["diagram_rows"] = len(diags or [])
    idx686 = next((d["i"] for d in (diags or []) if d["uid"] == D686), None)
    R["M4"]["d686_index"] = idx686
    fact("M4 Diagram census: %d row(s) ; Diagram #686 sits at traverse index %r"
         % (len(diags or []), idx686))
    R["M4"]["objects"] = {}
    for label, uid in M4_OBJECTS:
        (cls, ouid), err = safe("M4 owner_of(#%r)" % uid, lambda u=uid: owner_of(SCRATCH, u),
                                (None, None))
        oidx, _ = safe("M4 diag_index(#%r)" % ouid,
                       lambda u=ouid: diag_index(SCRATCH, u)) if ouid else (None, "")
        rec = {"uid": uid, "owner_class": cls, "owner_uid": ouid, "owner_diagram_index": oidx,
               "owner_is_686": (ouid == D686), "error": err}
        R["M4"]["objects"][label] = rec
        fact("M4 %-32s #%-7r owner = %r #%r (Diagram traverse index %r) ; owner IS #686? %r%s"
             % (label, uid, cls, ouid, oidx, (ouid == D686), ((" ERROR " + err) if err else "")))
    # the Global consumer's LIVE Nodes[] index and terminal table - resolved by uid, never carried
    hints = [idx686, 0, 19]
    for label, uid in (("Global #7202", 7202), ("FlatSequenceInnerTunnel #7468", 7468)):
        if left_s() < 120:
            fact("M4 %s: deadline reserve reached before the Nodes[] lookup - reported, not guessed"
                 % label)
            continue
        loc = find_node(SCRATCH, uid, hints, "M4 %s" % label, budget_s=150.0, quiet=True)
        f = loc.get("found") or {}
        R["M4"].setdefault("located", {})[label] = f
        fact("M4 %s LIVE LOOKUP: diagram #%r (traverse index %r), Nodes[%r], label %r, %d diagram(s) "
             "scanned" % (label, f.get("diagram_uid"), f.get("diagram_index"), f.get("nodes_index"),
                          f.get("label"), len(loc.get("scanned", []))))
        if f.get("nodes_index") is None:
            fact("M4 %s is NOT a member of any scanned diagram's Nodes[] - no terminal table exists "
                 "for it over this COM path (the same limit gscript.py:948 states)" % label)
            continue
        tt = terms_at(SCRATCH, f["diagram_index"], f["nodes_index"], uid, "M4 %s" % label, quiet=True)
        R["M4"].setdefault("terminals", {})[label] = tt
        fact("M4 %s terminal table (uid echo %r): %d terminal(s)"
             % (label, tt.get("uid_echo"), len(tt.get("terminals", []))))
        for t in tt.get("terminals", []):
            fact("    M4 %s t%-2d name=%-28r is_source=%-5r wire=%-7r state=%s"
                 % (label, t["i"], t["name"], t["is_source"], t["wire"], term_state(t)))


# ================================================================== [M3] the nets
def phase_m3():
    head("[M3] THE NETS - full membership of wires 4859 and 7506 by TERMINAL-SIDE reverse census")
    R["M3"]["method"] = (
        "TERMINAL-SIDE reverse census, the shape of tools/bench/diag_c62_branch.py:532-588: every "
        "Nodes[] terminal of the wires' OWN diagram (node_terms_uid), every front-panel terminal "
        "(panel_wiring), every shift-register terminal of both loops (already read in M1/M2), and a "
        "bounded LoopTunnel sweep (gscript.tunnels). A wire-side reader is run SEPARATELY and "
        "labelled; it is not the answer.")
    fact("M3 METHOD: %s" % R["M3"]["method"])
    hits = {}
    for w in NET_WIRES:
        hits[w] = []
    # which diagram owns each wire
    R["M3"]["wire_owner"] = {}
    diag_idxs = []
    for w in NET_WIRES:
        (cls, ouid), err = safe("M3 owner_of(w%d)" % w, lambda ww=w: owner_of(SCRATCH, ww),
                                (None, None))
        di, _ = safe("M3 diag_index(#%r)" % ouid, lambda u=ouid: diag_index(SCRATCH, u)) \
            if ouid else (None, "")
        R["M3"]["wire_owner"][w] = {"owner_class": cls, "owner_uid": ouid, "diagram_index": di,
                                    "error": err}
        fact("M3 wire %d is owned by %r #%r (Diagram traverse index %r)%s"
             % (w, cls, ouid, di, ((" ERROR " + err) if err else "")))
        if di is not None and di not in diag_idxs:
            diag_idxs.append(di)
    if not diag_idxs:
        fact("M3 no owning diagram resolved for either wire - the census cannot be scoped; reported")
        return
    cls_by_uid = {}
    rows_map, _ = safe("M3 report_all('Node')", lambda: g.report_all(SCRATCH, "Node"), [])
    for o in (rows_map or []):
        cls_by_uid[o["uid"]] = o["class"]
    R["M3"]["node_class_map"] = len(cls_by_uid)
    fact("M3 Node class map: %d entries" % len(cls_by_uid))
    R["M3"]["scans"] = []
    for di in diag_idxs:
        labels, lerr = safe("M3 node_labels(%d)" % di, lambda k=di: g.node_labels(SCRATCH, k), [])
        n_max = min(len(labels or []), NODE_CENSUS_CAP)
        scan = {"diagram_index": di, "nodes": len(labels or []), "cap": n_max,
                "label_error": lerr, "scanned": 0, "errors": []}
        fact("M3 scanning Diagram traverse index %d: %d node(s), cap %d%s"
             % (di, len(labels or []), n_max, ((" ERROR " + lerr) if lerr else "")))
        for n in range(n_max):
            if left_s() < 90:
                scan["stopped"] = "deadline reserve reached after %d node(s)" % scan["scanned"]
                fact("M3 %s - census TRUNCATED, reported not guessed" % scan["stopped"])
                break
            scan["scanned"] += 1
            try:
                node_uid, trows = g.node_terms_uid(SCRATCH, di, n)
            except Exception as e:                                                # noqa: BLE001
                scan["errors"].append({"n": n, "error": str(e)[:160]})
                continue
            if not node_uid:
                break
            for t in trows:
                if t["wire"] and t["wire"] in hits:
                    hits[t["wire"]].append(
                        {"owner_uid": node_uid, "owner_class": cls_by_uid.get(node_uid),
                         "owner_label": labels[n]["label"] if n < len(labels or []) else None,
                         "nodes_index": n, "terminal_index": t["i"], "terminal_name": t["name"],
                         "terminal_name_hex": (t["name"] or "").encode("utf-8").hex(),
                         "is_source": t["is_source"], "via": "Nodes[] terminal census"})
        scan["truncated"] = (len(labels or []) > n_max) or bool(scan.get("stopped"))
        R["M3"]["scans"].append(scan)
    # front-panel terminals
    prows, perr = safe("M3 panel_wiring", lambda: g.panel_wiring(SCRATCH), [])
    R["M3"]["panel_rows"] = len(prows or [])
    fact("M3 panel_wiring: %d front-panel row(s)%s"
         % (len(prows or []), ((" ERROR " + perr) if perr else "")))
    for r in (prows or []):
        if r["wire"] and r["wire"] in hits:
            hits[r["wire"]].append(
                {"owner_uid": r["uid"], "owner_class": "PANEL OBJECT (panel_wiring row)",
                 "owner_label": r["label"], "nodes_index": None, "terminal_index": None,
                 "terminal_name": r["label"], "terminal_name_hex": (r["label"] or "").encode("utf-8").hex(),
                 "is_source": r["is_source"], "via": "panel_wiring row"})
    # shift-register terminals already read in M1 / M2
    for tag, key in (("M1 loop#637", "M1"), ("M2 loop#23032", "M2")):
        for t in (R[key].get("terminals") or []):
            if t["wire"] and t["wire"] in hits:
                hits[t["wire"]].append(
                    {"owner_uid": t["uid"], "owner_class": t["class"], "owner_label": tag,
                     "nodes_index": None, "terminal_index": None, "terminal_name": t["name"],
                     "terminal_name_hex": (t["name"] or "").encode("utf-8").hex(),
                     "is_source": t["is_source"], "via": "shift-register census (%s)" % t["terminal"]})
    # a bounded LoopTunnel sweep - LoopTunnels are not Nodes[] members either
    R["M3"]["tunnel_sweep"] = {"scanned": 0, "truncated": False}
    for i in range(TUNNEL_CAP):
        if left_s() < 60:
            R["M3"]["tunnel_sweep"]["truncated"] = True
            R["M3"]["tunnel_sweep"]["stopped"] = "deadline reserve reached at index %d" % i
            break
        tn, terr = safe("M3 tunnels(%d)" % i, lambda k=i: g.tunnels(SCRATCH, k))
        if terr or not tn or not tn.get("uid"):
            break
        R["M3"]["tunnel_sweep"]["scanned"] = i + 1
        if tn["out_wire"] and tn["out_wire"] in hits:
            hits[tn["out_wire"]].append(
                {"owner_uid": tn["uid"], "owner_class": "LoopTunnel", "owner_label": None,
                 "nodes_index": None, "terminal_index": None, "terminal_name": tn["out_name"],
                 "terminal_name_hex": (tn["out_name"] or "").encode("utf-8").hex(),
                 "is_source": tn["out_is_source"], "via": "tunnels() OUTER"})
        for k, wv in enumerate(tn.get("in_wires") or []):
            if wv and wv in hits:
                nm = (tn.get("in_names") or [""] * (k + 1))[k] if k < len(tn.get("in_names") or []) else ""
                src = (tn.get("in_is_source") or [None] * (k + 1))[k] \
                    if k < len(tn.get("in_is_source") or []) else None
                hits[wv].append(
                    {"owner_uid": tn["uid"], "owner_class": "LoopTunnel", "owner_label": None,
                     "nodes_index": None, "terminal_index": k, "terminal_name": nm,
                     "terminal_name_hex": (nm or "").encode("utf-8").hex(),
                     "is_source": src, "via": "tunnels() INSIDE[%d]" % k})
    else:
        R["M3"]["tunnel_sweep"]["truncated"] = True
    fact("M3 LoopTunnel sweep: %d tunnel(s) read, truncated %r"
         % (R["M3"]["tunnel_sweep"]["scanned"], R["M3"]["tunnel_sweep"]["truncated"]))
    # the answer
    R["M3"]["nets"] = {}
    for w in NET_WIRES:
        rowlist = hits[w]
        named = CONSUMERS.get(w, ("", 0, ""))
        sinks = [h for h in rowlist if h["is_source"] is False]
        sources = [h for h in rowlist if h["is_source"] is True]
        other_sinks = [h for h in sinks if h["owner_uid"] != named[1]]
        R["M3"]["nets"][w] = {"terminal_count": len(rowlist), "rows": rowlist,
                              "sources": len(sources), "sinks": len(sinks),
                              "named_consumer": {"class": named[0], "uid": named[1],
                                                 "terminal_name": named[2]},
                              "sinks_other_than_the_named_consumer": other_sinks}
        fact("M3 NET of wire %d: EXACTLY %d terminal(s) found by the terminal-side census "
             "(%d source, %d sink)" % (w, len(rowlist), len(sources), len(sinks)))
        for h in rowlist:
            fact("    M3 net %d <- owner #%-7r %-26r label=%-28r Nodes[%r] t%r name=%r "
                 "is_source=%r via %s"
                 % (w, h["owner_uid"], h["owner_class"], h["owner_label"], h["nodes_index"],
                    h["terminal_index"], h["terminal_name"], h["is_source"], h["via"]))
        fact("M3 NET %d: sink(s) OTHER THAN the named consumer %s #%d -> %d : %r"
             % (w, named[0], named[1], len(other_sinks),
                [(h["owner_class"], h["owner_uid"], h["terminal_name"]) for h in other_sinks]))
    # the labelled SECONDARY wire-side reading
    head("[M3b] SECONDARY, labelled: the WIRE-SIDE reader on the same two wires (not the answer)")
    R["M3"]["wire_side"] = {}
    for w in NET_WIRES:
        R["M3"]["wire_side"][w] = wire_walk(w, "M3b")
        cen = R["M3"]["nets"].get(w, {}).get("terminal_count")
        wsr = R["M3"]["wire_side"][w].get("real_owner_rows")
        fact("M3b wire %d: terminal-side census %r terminal(s) vs wire-side reader %r real-owner "
             "row(s) - AGREE? %r" % (w, cen, wsr, cen == wsr))


# ================================================================== [6] hygiene
def phase_hygiene():
    head("[6] HYGIENE - close the scratch, delete it, re-read every pin, handles at both ends")
    safe("close_panel(scratch)", lambda: g.close_panel(SCRATCH))
    R["M6"]["ref_counts"] = g.ref_counts()
    fact("M6 gscript ref_counts (refs opened / closed / live): %r" % R["M6"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         R["M6"]["ref_counts"]["live"] == 0, "%r" % R["M6"]["ref_counts"])
    gate("H6 every OpWireSource_v5 row echoed recip == the queried wire uid (Pre-decided 85)",
         R["pd85_violation_total"] == 0, "%d violation(s)" % R["pd85_violation_total"])
    handles, _ = safe("handles after", labview_handles)
    R["M6"]["handles_after_reads"] = handles
    fact("M6 LabVIEW handle count AFTER the reads: %r (after the restart it was %r ; baseline "
         "~31,500)" % (handles, R["M6"].get("handles_after_restart")))
    _, err = safe("restart_labview before delete", restart_labview)
    g.reset()
    time.sleep(2.0)
    ok = True
    for attempt in range(6):
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
            break
        except Exception as e:                                                    # noqa: BLE001
            ok = False
            fact("scratch delete attempt %d failed: %s" % (attempt + 1, str(e)[:120]))
            time.sleep(4.0)
    gate("H4 the scratch copy is deleted", not os.path.exists(SCRATCH),
         "%s%s" % (SCRATCH, ("" if ok else " (needed retries)")))
    got = md5(ARTEFACT)
    R["artefact_md5_after"] = got
    gate("H2 artefact md5 UNCHANGED after the run", got == R.get("artefact_md5_before"),
         "before %s / after %s" % (R.get("artefact_md5_before"), got))
    allpins = True
    R["pins_after"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_after"][label] = have
        allpins = allpins and (have == want)
        fact("PIN AFTER  %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the four STATUS md5 pins all hold", allpins)
    handles2, _ = safe("handles final", labview_handles)
    R["M6"]["handles_final"] = handles2
    fact("M6 LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c75_m3a3_rows - MEASUREMENT ONLY, hygiene gates only (Pre-decided 63)",
          flush=True)
    print("=" * 100, flush=True)
    try:
        phase_0()
        phase_m5()
        phase_1()
        phase_m1()
        phase_m2()
        phase_m4()
        phase_m3()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        R["fatal"] = traceback.format_exc()[-2000:]
        fact("FATAL (a defect in THIS PYTHON SCRIPT or an unhandled read error, NOT a refusal by "
             "LabVIEW) %s: %s" % (type(e).__name__, str(e)[:200]))
    finally:
        try:
            phase_hygiene()
        except Exception as e:                                                    # noqa: BLE001
            import traceback
            R["hygiene_fatal"] = traceback.format_exc()[-1500:]
            gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES: %d pass / %d fail%s"
          % (len(passes), len(fails), (("  FAILING: " + ", ".join(fails)) if fails else "")),
          flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
