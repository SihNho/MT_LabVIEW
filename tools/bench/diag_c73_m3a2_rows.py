"""DIAGNOSTIC, MEASUREMENT ONLY — the M3a-2 row table (initial values of the two new shift registers).

WHAT THIS IS NOT: it builds nothing, it creates no op, it edits no deliverable. It COPIES the M3a-1
artefact to a unique scratch name, reads the scratch, deletes the scratch, and re-reads the artefact's
md5 to prove it is byte-unchanged. Per `docs/cycle27-plan.md` Pre-decided 63 a measurement-only
diagnostic GATES ON HYGIENE ONLY: a negative measurement is a FACT line, never a failing gate.

PRIOR ART CHECKED BEFORE WRITING A LINE (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/gscript.py` — `shift_reg` :783 / `shift_reg_left` :816 (OpShiftRegs_v0/v1) give a register's
    uid, class, outer terminal and inside terminals; `node_terms` :900 (OpNodeTerms_v0) gives a node's
    full terminal table; `report_all` :502, `count` :1035, `exec_state` :2007, `ensure_loaded` :1298.
  * `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` — the ONLY by-UID walk of a
    WIRE's terminals; REPAIRED 2026-09-22 (indicators scrubbed, all 8 error outs read, uid echo
    required). Acceptance `tools/bench/diag_c68_echo_accept.log`.
  * `tools/recipes/build_d1_v0.py` — `owner_of` :338 (OpOwnerChain_v1, strict uid echo) and
    `diag_index` :357.
  * `tools/recipes/build_d1_m3a1.py` — `find_node` :541, `terms_at` :500, `node_view` :572,
    `term_state` :524, `safe` :442 are re-used by import (they take the path as a parameter).
  * `tools/bench/main_vi_shiftregs_v1.json` — the RECORDED register table of WhileLoop #637 in the
    ORIGINAL (14 registers; [1]=#4256/#4274 position, [2]=#4334/#4344 VISA). Used ONLY as a comparison
    value: every number below is re-read from the live scratch.
NOTHING NEW IS BUILT (user, 2026-09-18 08:53 "장치는 더 만들지 말고 계속 진행").

PREDICTION CONTRACT (the hygiene gates; these are the only things that can FAIL):
  H1  the artefact's md5 is `6b3c1f3c4ba80f1fa7411a55f0218bea` BEFORE the run.
  H2  the artefact's md5 is unchanged AFTER the run (the artefact is never opened, only copied).
  H3  the four STATUS md5 pins (ORIGINAL, S1, S2, THE BED) all hold after the run.
  H4  the scratch copy is deleted and no longer on disk.
  H5  gscript's in-process VI-Server reference counter is level (opened == closed) at exit.
MEASUREMENT EXPECTATIONS (recorded, NOT gated — a mismatch is reported as a FACT):
  E1  loop #23032 carries exactly 2 shift registers, uids #23868 (VISA) and #23895 (POS).
  E2  loop #637 carries 14, with [1] = #4256/#4274 and [2] = #4334/#4344.
  E3  #4344's outer wire is 4185 and #4274's is 3968 (the two INITIAL-VALUE feeds).
  E4  #4334's outer wire is 7506 and #4256's is 4859 (the two right-side OUTER consumers).
  E5  diagram #686 carries both WhileLoop #637 and WhileLoop #23032.
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
ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_BROKEN_20260922_005732.vi")
ARTEFACT_MD5 = "6b3c1f3c4ba80f1fa7411a55f0218bea"
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C73SCRATCH_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c73_m3a2_rows.json")

LOOP_A = 23032                    # the NEW While loop (M3a-1's registers live on it)
LOOP_11 = 637                     # the ORIGINAL While loop that owns Diagram #639
D686 = 686                        # the diagram said to carry both loops - MEASURED below
NEW_REGS = {"VISA": 23868, "POS": 23895}
OLD_PAIRS = {"POS": {"reg_index": 1, "right": 4256, "left": 4274},
             "VISA": {"reg_index": 2, "right": 4334, "left": 4344}}
SET_UIDS = [3529, 3560, 3447, 48, 10407, 23499, 23523]   # the seven moved nodes (build_d1_m3a1.SET)
BODY_A = 23058
REG_PROBE_MAX = 16
RUN_DEADLINE_S = 40 * 60.0
RESERVE_S = 180.0

T0 = time.time()
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "scratch": SCRATCH,
     "artefact": ARTEFACT, "F1": {}, "F2": {}, "F3": {}, "F4": {}, "F7": {}, "hash_probe": []}
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
    """Every shift register of one loop, READ: right uid/class + outer/inside terminals, and the same
    for its LEFT partner (shift_reg_left / OpShiftRegs_v1). Stops at the first slot that errors."""
    out = []
    for k in range(cap):
        sr, err = safe("%s shift_reg_left(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg_left(SCRATCH, loop_index, kk))
        if err or not sr:
            fact("%s reg_index=%d -> READ ERROR %s" % (tag, k, err))
            break
        row = {"reg_index": k, "right_uid": sr.get("uid"), "right_class": sr.get("class"),
               "right_out": sr.get("out"), "right_inside": sr.get("inside"),
               "left_uids": sr.get("left_uids"), "left_uid": (sr.get("left") or {}).get("uid"),
               "left_class": (sr.get("left") or {}).get("class"),
               "left_out": (sr.get("left") or {}).get("out"),
               "left_inside": (sr.get("left") or {}).get("inside"),
               "op_errors": sr.get("errors")}
        out.append(row)
        fact("%s reg_index=%d RIGHT #%r %r outer=%r inside=%r | LEFT #%r %r outer=%r inside=%r | errors=%r"
             % (tag, k, row["right_uid"], row["right_class"], row["right_out"], row["right_inside"],
                row["left_uid"], row["left_class"], row["left_out"], row["left_inside"], row["op_errors"]))
        if row["op_errors"]:
            break
        if row["right_uid"] in (None, 0):
            break
    return out


def wire_walk(wire_uid, tag, n=8):
    """Every terminal on one wire, by UID (OpWireSource_v5 through the repaired wrapper). Reports the
    Pre-decided 85 precondition per row: a real-owner row must echo recip == the queried wire uid."""
    rec = {"wire": wire_uid, "rows": [], "pd85_violations": [], "error": ""}
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
            if r.get("recip") != wire_uid:
                rec["pd85_violations"].append(r)
            fact("    %s w%-7r t%-2d is_source=%-5r owner_class=%-22r owner_uid=%-7r recip=%r%s"
                 % (tag, wire_uid, r["i"], r.get("is_source"), r.get("owner_class"), r.get("owner_uid"),
                    r.get("recip"), "  PD85 VIOLATION" if r.get("recip") != wire_uid else ""))
        else:
            fact("    %s w%-7r t%-2d NO OWNER  %r" % (tag, wire_uid, r["i"],
                                                      (r.get("err") or "")[:110]))
    rec["real_owner_rows"] = real
    fact("%s wire %r: %d row(s), %d with a REAL owner, %d PD85 violation(s)"
         % (tag, wire_uid, len(rows or []), real, len(rec["pd85_violations"])))
    return rec


def name_terminal(owner_uid, owner_class, wire_uid, tag, hints):
    """The TERMINAL NAME behind one owner row: locate the owner in some diagram's Nodes[] and read its
    terminal table, then pick the terminal carrying `wire_uid`. Structure-border classes (shift
    registers, tunnels) are NOT Nodes[] members - that is reported as a fact, never guessed."""
    rec = {"owner_uid": owner_uid, "owner_class": owner_class, "wire": wire_uid}
    if owner_class in ("LeftShiftRegister", "RightShiftRegister", "LoopTunnel", "Tunnel",
                       "SelectorTunnel", "ControlTerminal"):
        rec["terminal_name"] = None
        rec["why"] = ("%s is a structure-border object, not a member of any diagram's Nodes[]; "
                      "node_terms cannot name it (gscript.py:948)" % owner_class)
        fact("%s owner #%r (%s): no terminal name - %s" % (tag, owner_uid, owner_class, rec["why"]))
        return rec
    if left_s() < 60:
        rec["why"] = "deadline reserve reached; lookup skipped"
        fact("%s owner #%r (%s): %s" % (tag, owner_uid, owner_class, rec["why"]))
        return rec
    loc = find_node(SCRATCH, owner_uid, hints, "%s owner #%r" % (tag, owner_uid), budget_s=90.0,
                    quiet=True)
    f = loc.get("found") or {}
    rec["located"] = f
    if f.get("nodes_index") is None:
        rec["terminal_name"] = None
        rec["why"] = "not found in any scanned diagram's Nodes[] (%d scanned)" % len(loc.get("scanned", []))
        fact("%s owner #%r (%s): %s" % (tag, owner_uid, owner_class, rec["why"]))
        return rec
    tt = terms_at(SCRATCH, f["diagram_index"], f["nodes_index"], owner_uid,
                  "%s owner #%r" % (tag, owner_uid), quiet=True)
    hit = [t for t in tt.get("terminals", []) if t.get("wire") == wire_uid]
    rec["terminal_rows"] = hit
    rec["terminal_name"] = hit[0]["name"] if hit else None
    rec["diagram_uid"] = f.get("diagram_uid")
    rec["node_label"] = f.get("label")
    fact("%s owner #%r (%s) label %r on Diagram #%r: terminal(s) carrying w%r -> %r"
         % (tag, owner_uid, owner_class, f.get("label"), f.get("diagram_uid"), wire_uid,
            [(t["i"], t["name"], t["is_source"]) for t in hit]))
    return rec


# ================================================================== [0] files only, zero LabVIEW
def phase_0():
    head("[0] FILES ONLY - the artefact's md5 BEFORE anything, and the four pins")
    got = md5(ARTEFACT)
    R["artefact_md5_before"] = got
    gate("H1 artefact md5 before == %s" % ARTEFACT_MD5, got == ARTEFACT_MD5, "got %s" % got)
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s" % (label, have, want, "OK" if have == want else "DIFFERS"))
    for tag, path in (("artefact", ARTEFACT),):
        line = HASH(path)
        R["hash_probe"].append({"tag": tag, "line": line})
        fact("hash_probe %s: %s" % (tag, line))


# ================================================================== [1] restart + the scratch copy
def phase_1():
    head("[1] RESTART LabVIEW (STATUS: left running after run 5), then the scratch copy")
    before, _ = safe("handles before restart", labview_handles)
    R["handles_before_restart"] = before
    fact("LabVIEW handle count BEFORE the restart: %r" % before)
    _, err = safe("restart_labview", restart_labview)
    R["restart_error"] = err
    g.reset()
    time.sleep(3.0)
    after, _ = safe("handles after restart", labview_handles)
    R["handles_after_restart"] = after
    fact("LabVIEW handle count AFTER the restart: %r" % after)
    shutil.copyfile(ARTEFACT, SCRATCH)
    time.sleep(0.4)
    R["scratch_md5"] = md5(SCRATCH)
    fact("scratch %s md5 %s (copy of the artefact, %d bytes)"
         % (os.path.basename(SCRATCH), R["scratch_md5"], os.path.getsize(SCRATCH)))
    t = time.time()
    _, err = safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("ensure_loaded(scratch) took %.1f s%s" % (time.time() - t, (" ERROR " + err) if err else ""))
    es, _ = safe("exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state_cold"] = es
    fact("F4 ExecState of the scratch (= the artefact) = %r" % es)


# ================================================================== [2] F1 - the two NEW registers
def phase_f1():
    head("[2] F1 - the two registers `add_shift_reg` created on loop #23032 in run 5")
    li = loop_index_of(LOOP_A, "F1")
    R["F1"]["loop_index"] = li
    if li is None:
        fact("F1 loop #%d NOT RESOLVED - the rest of F1 cannot be read" % LOOP_A)
        return
    tbl = reg_table(li, "F1 loop#23032")
    R["F1"]["registers"] = tbl
    fact("F1 loop #23032 carries %d shift register(s); right uids %r ; left uids %r"
         % (len(tbl), [r["right_uid"] for r in tbl], [r["left_uid"] for r in tbl]))
    for pair, want in NEW_REGS.items():
        hit = next((r for r in tbl if r["right_uid"] == want), None)
        fact("F1 %s pair: build log says right uid #%d -> %s"
             % (pair, want, ("reg_index %d, left #%r" % (hit["reg_index"], hit["left_uid"]))
                if hit else "NOT PRESENT in the live table"))
    # every terminal of each register, flattened, with BARE marked
    flat = []
    for r in tbl:
        for side, uid, cls, o, ins in (("RIGHT", r["right_uid"], r["right_class"], r["right_out"], r["right_inside"]),
                                       ("LEFT", r["left_uid"], r["left_class"], r["left_out"], r["left_inside"])):
            if o is not None:
                flat.append({"reg_index": r["reg_index"], "side": side, "uid": uid, "class": cls,
                             "terminal": "OUTER", "name": o.get("name"), "is_source": o.get("is_source"),
                             "wire": o.get("wire") or "bare"})
            for k, t in enumerate(ins or []):
                flat.append({"reg_index": r["reg_index"], "side": side, "uid": uid, "class": cls,
                             "terminal": "INSIDE[%d]" % k, "name": t.get("name"),
                             "is_source": t.get("is_source"), "wire": t.get("wire") or "bare"})
    R["F1"]["terminals"] = flat
    for t in flat:
        fact("F1 TERM reg%d %-5s #%-6r %-19s %-9s name=%-30r is_source=%-5r wire=%r"
             % (t["reg_index"], t["side"], t["uid"], t["class"], t["terminal"], t["name"],
                t["is_source"], t["wire"]))


# ================================================================== [3] F2 - the ORIGINAL rows
def phase_f2():
    head("[3] F2 - the ORIGINAL registers of loop #637 and the wires they sit on")
    li = loop_index_of(LOOP_11, "F2")
    R["F2"]["loop_index"] = li
    if li is None:
        fact("F2 loop #%d NOT RESOLVED - the rest of F2 cannot be read" % LOOP_11)
        return
    tbl = reg_table(li, "F2 loop#637")
    R["F2"]["registers"] = tbl
    fact("F2 loop #637 carries %d shift register(s); right uids %r"
         % (len(tbl), [r["right_uid"] for r in tbl]))
    R["F2"]["pairs"] = {}
    for pair, want in OLD_PAIRS.items():
        hit = next((r for r in tbl if r["right_uid"] == want["right"]), None)
        rec = {"want": want, "found": bool(hit)}
        R["F2"]["pairs"][pair] = rec
        if not hit:
            fact("F2 %s pair: RightShiftRegister #%d NOT in the live table - measured absent"
                 % (pair, want["right"]))
            continue
        rec["reg_index"] = hit["reg_index"]
        rec["right_uid"], rec["left_uid"] = hit["right_uid"], hit["left_uid"]
        rec["left_uid_matches_plan"] = (hit["left_uid"] == want["left"])
        rec["right_outer"] = hit["right_out"]
        rec["left_outer"] = hit["left_out"]
        fact("F2 %s pair MEASURED: reg_index %d ; RIGHT #%r ; LEFT #%r (plan says #%d ; equal %r)"
             % (pair, hit["reg_index"], hit["right_uid"], hit["left_uid"], want["left"],
                rec["left_uid_matches_plan"]))
        # (i) the INITIAL-VALUE side: the LEFT register's OUTER terminal
        lw = (hit["left_out"] or {}).get("wire") or 0
        fact("F2 %s (i) the LEFT register #%r OUTER terminal: name=%r is_source=%r wire=%r  <- THE "
             "INITIAL VALUE M3a-2 MUST COPY" % (pair, hit["left_uid"], (hit["left_out"] or {}).get("name"),
                                                (hit["left_out"] or {}).get("is_source"), lw or "bare"))
        rec["initial_wire"] = lw
        rec["initial_walk"] = wire_walk(lw, "F2 %s (i) initial-value wire" % pair)
        rec["initial_sources"] = [r for r in rec["initial_walk"]["rows"]
                                  if r.get("owner_uid") and r.get("is_source")]
        fact("F2 %s (i) SOURCE terminal(s) on the initial-value wire %r: %r"
             % (pair, lw, [(r["owner_class"], r["owner_uid"]) for r in rec["initial_sources"]]))
        rec["initial_source_names"] = [
            name_terminal(r["owner_uid"], r["owner_class"], lw, "F2 %s (i)" % pair, [19, 0, 48])
            for r in rec["initial_sources"]]
        rec["initial_owner_diagrams"] = {}
        # (ii) the RIGHT partner's OUTER side: what the original drives downstream of the loop
        rw = (hit["right_out"] or {}).get("wire") or 0
        fact("F2 %s (ii) the RIGHT register #%r OUTER terminal: name=%r is_source=%r wire=%r  <- what "
             "the ORIGINAL feeds downstream of the loop (rule 1a / plan item 69)"
             % (pair, hit["right_uid"], (hit["right_out"] or {}).get("name"),
                (hit["right_out"] or {}).get("is_source"), rw or "bare"))
        rec["right_outer_wire"] = rw
        rec["right_walk"] = wire_walk(rw, "F2 %s (ii) right-outer wire" % pair)
        rec["right_sinks"] = [r for r in rec["right_walk"]["rows"]
                              if r.get("owner_uid") and not r.get("is_source")]
        fact("F2 %s (ii) SINK terminal(s) on the right-outer wire %r: %r"
             % (pair, rw, [(r["owner_class"], r["owner_uid"]) for r in rec["right_sinks"]]))
        rec["right_sink_names"] = [
            name_terminal(r["owner_uid"], r["owner_class"], rw, "F2 %s (ii)" % pair, [19, 0, 48])
            for r in rec["right_sinks"]]


# ================================================================== [4] F3 - diagram membership
def phase_f3():
    head("[4] F3 - which DIAGRAM each object lives on (owner chain, strict uid echo)")
    diags, err = safe("F3 report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    R["F3"]["diagram_rows"] = len(diags or [])
    idx686 = next((d["i"] for d in (diags or []) if d["uid"] == D686), None)
    R["F3"]["d686_index"] = idx686
    fact("F3 Diagram census: %d row(s) ; Diagram #686 sits at index %r" % (len(diags or []), idx686))
    # the two loops
    R["F3"]["loops"] = {}
    for uid in (LOOP_11, LOOP_A):
        loc = find_node(SCRATCH, uid, [idx686, 0, 19], "F3 loop #%d" % uid, budget_s=150.0, quiet=True)
        f = loc.get("found") or {}
        R["F3"]["loops"][uid] = f
        fact("F3 WhileLoop #%d border lives on Diagram #%r (index %r, class %r, Nodes[%r], label %r) - "
             "is that #686? %r" % (uid, f.get("diagram_uid"), f.get("diagram_index"),
                                   f.get("diagram_class"), f.get("nodes_index"), f.get("label"),
                                   f.get("diagram_uid") == D686))
    # the wires named by F2, via OpOwnerChain_v1 (a wire's owner IS its diagram)
    R["F3"]["wires"] = {}
    for pair, rec in (R["F2"].get("pairs") or {}).items():
        for which in ("initial_wire", "right_outer_wire"):
            w = rec.get(which) or 0
            if not w:
                continue
            (cls, ouid), err = safe("F3 owner_of(w%r)" % w, lambda ww=w: owner_of(SCRATCH, ww),
                                    (None, None))
            R["F3"]["wires"]["%s.%s" % (pair, which)] = {"wire": w, "owner_class": cls,
                                                         "owner_uid": ouid, "error": err}
            fact("F3 wire %r (%s %s) is owned by %r #%r - on Diagram #686? %r"
                 % (w, pair, which, cls, ouid, ouid == D686))
    # every owner named on the initial-value walks
    for pair, rec in (R["F2"].get("pairs") or {}).items():
        for r in rec.get("initial_sources", []):
            (cls, ouid), err = safe("F3 owner_of(#%r)" % r["owner_uid"],
                                    lambda u=r["owner_uid"]: owner_of(SCRATCH, u), (None, None))
            fact("F3 %s initial-value SOURCE owner #%r (%s) is owned by %r #%r%s"
                 % (pair, r["owner_uid"], r["owner_class"], cls, ouid, (" ERROR " + err) if err else ""))


# ================================================================== [5] F4 - bare-terminal census
def phase_f4():
    head("[5] F4 - the bare-terminal census of the seven moved nodes + the two new registers")
    diags, _ = safe("F4 report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    body_idx = next((d["i"] for d in (diags or []) if d["uid"] == BODY_A), None)
    R["F4"]["body_diagram_index"] = body_idx
    fact("F4 the body diagram #%d of loop #23032 sits at Diagram index %r" % (BODY_A, body_idx))
    labels, err = safe("F4 node_labels(body)", lambda: g.node_labels(SCRATCH, body_idx), []) \
        if body_idx is not None else ([], "body diagram not found")
    by_uid = {r["uid"]: r for r in (labels or [])}
    fact("F4 the body diagram lists %d node(s)%s" % (len(labels or []), (" ERROR " + err) if err else ""))
    R["F4"]["nodes"] = {}
    total_bare = 0
    for uid in SET_UIDS:
        if left_s() < 45:
            fact("F4 deadline reserve reached before #%r - census incomplete, reported as a fact" % uid)
            break
        row = by_uid.get(uid)
        if row is None:
            loc = find_node(SCRATCH, uid, [body_idx, 19, 0], "F4 #%r" % uid, budget_s=90.0, quiet=True)
            f = loc.get("found") or {}
            di, ni = f.get("diagram_index"), f.get("nodes_index")
            where = f.get("diagram_uid")
        else:
            di, ni = body_idx, [r["uid"] for r in labels].index(uid)
            where = BODY_A
        if ni is None:
            R["F4"]["nodes"][uid] = {"found": False}
            fact("F4 node #%r NOT LOCATED - reported, not guessed" % uid)
            continue
        tt = terms_at(SCRATCH, di, ni, uid, "F4 #%r" % uid, quiet=True)
        rows = tt.get("terminals", [])
        bare = [t for t in rows if term_state(t) == "BARE"]
        unread = [t for t in rows if term_state(t) == "UNREAD"]
        total_bare += len(bare)
        R["F4"]["nodes"][uid] = {"diagram_uid": where, "diagram_index": di, "nodes_index": ni,
                                 "uid_echo": tt.get("uid_echo"), "terminals": len(rows),
                                 "bare": [(t["i"], t["name"], t["is_source"]) for t in bare],
                                 "unread": [(t["i"], t["name"]) for t in unread]}
        fact("F4 node #%-6r on Diagram #%r (echo %r): %d terminal(s), %d BARE %r, %d UNREAD %r"
             % (uid, where, tt.get("uid_echo"), len(rows), len(bare),
                [(t["i"], t["name"], "src" if t["is_source"] else "sink") for t in bare],
                len(unread), [(t["i"], t["name"]) for t in unread]))
    R["F4"]["total_bare_on_moved_nodes"] = total_bare
    fact("F4 TOTAL bare terminals across the located moved nodes: %d" % total_bare)
    # the two new registers' bare terminals, from F1's flattened table
    regbare = [t for t in (R["F1"].get("terminals") or []) if t.get("wire") == "bare"]
    R["F4"]["register_bare"] = regbare
    fact("F4 BARE terminals on the two NEW registers: %d -> %r"
         % (len(regbare), [(t["side"], t["uid"], t["terminal"]) for t in regbare]))
    es, _ = safe("F4 exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["F4"]["exec_state"] = es
    fact("F4 ExecState of the scratch at the END of the reads = %r (cold read was %r)"
         % (es, R.get("exec_state_cold")))


# ================================================================== [6] hygiene
def phase_hygiene():
    head("[6] F7 HYGIENE - close the scratch, delete it, re-read every pin")
    safe("close_panel(scratch)", lambda: g.close_panel(SCRATCH))
    R["F7"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts: %r" % R["F7"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         R["F7"]["ref_counts"]["live"] == 0, "%r" % R["F7"]["ref_counts"])
    handles, _ = safe("handles after", labview_handles)
    R["F7"]["handles_after"] = handles
    fact("LabVIEW handle count AFTER the reads: %r (after restart it was %r)"
         % (handles, R.get("handles_after_restart")))
    # delete the scratch - restart LabVIEW first so nothing holds the file open
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
         "%s%s" % (SCRATCH, "" if ok else " (needed retries)"))
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
        fact("PIN AFTER  %-16s %s  (want %s) %s" % (label, have, want, "OK" if have == want else "DIFFERS"))
    gate("H3 the four STATUS md5 pins all hold", allpins)
    handles2, _ = safe("handles final", labview_handles)
    R["F7"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r" % handles2)


def main():
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c73_m3a2_rows - MEASUREMENT ONLY, hygiene gates only (Pre-decided 63)", flush=True)
    print("=" * 100, flush=True)
    try:
        phase_0()
        phase_1()
        phase_f1()
        phase_f2()
        phase_f3()
        phase_f4()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        R["fatal"] = traceback.format_exc()[-2000:]
        fact("FATAL %s: %s" % (type(e).__name__, str(e)[:200]))
    finally:
        try:
            phase_hygiene()
        except Exception as e:                                                    # noqa: BLE001
            import traceback
            R["hygiene_fatal"] = traceback.format_exc()[-1500:]
            gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                          ("  FAILING: " + ", ".join(fails)) if fails else ""), flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
