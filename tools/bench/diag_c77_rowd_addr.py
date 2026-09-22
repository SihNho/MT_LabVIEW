"""DIAGNOSTIC, MEASUREMENT ONLY - the c76b review's "cheapest discriminating measurement" for M3a-3 ROW D.

WHAT THIS IS NOT: it builds nothing, it creates no op, it edits no deliverable, it saves nothing, it runs no
deliverable VI. It COPIES the current bed to a unique scratch name, READS the scratch, deletes the scratch and
re-reads every md5 pin to prove nothing moved. Per `docs/cycle27-plan.md` Pre-decided 63 a measurement-only
diagnostic GATES ON HYGIENE ONLY: a negative measurement is a FACT line, never a failing gate. `ExecState` is
recorded once as a FACT and is NEVER a discriminator (the artefact is BROKEN BY DESIGN; Pre-decided 95, 42(c)).

WHAT IT MEASURES (exactly the four reads `archive/peer/2026-09-22-c76b-m3a3-run2-failpred.md` names under
"Cheapest discriminating measurement", plus the terminal-table read Pre-decided 107 prescribes):
  A  `OpFsInnerTunnelTerm_v0` (38/38 in `tools/bench/build_opfstunnelterm_v2_run1.log:160-161`) on uid 7468 -
     does it hand back a terminal reference? Raw return, class echo, every error column VERBATIM. A control
     read on another FlatSequenceInnerTunnel uid of the SAME target separates "op is broken here" from
     "7468 is special".
  B  `find_node` (the reader run 2's gate P0 used, build_d1_m3a1.py:541) on #43914 (nested FlatSequence),
     #12938 (top-level FlatSequence) and #681 itself. Both miss => the miss tracks the CLASS; 43914 found and
     12938 missed => it tracks the OWNER; both found => #681 is special. The per-diagram `scanned` rows are
     KEPT this time (the review's process note: run 2 discarded exactly the dataset that would have answered).
  C  `report_all(TARGET,'Diagram')` rows 0-3 - is row 0 still `TopLevelDiagram #536`, so "173 of 173 scanned"
     provably included the top level.
  D  the OWNING NODE's terminal table, Pre-decided 107's route: `FlatSequence #681` read as a NODE on
     `Diagram #686` (traverse idx 19), every entry listed with (index, name, is_source, connected wire), and
     the count of entries carrying wire 7506 stated explicitly as zero / one / more than one. When #681 is not
     a Nodes[] member a LABELLED SECONDARY sweep of every OTHER node of diagram 19 reports which terminals do
     carry 7506 - so the row-D sink question is answered either way.
  E  is CITED, not re-measured (Pre-decided 108): `tools/bench/diag_c75b_loopterms.log:73-83`.

PRIOR ART CHECKED BEFORE WRITING A LINE (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/diag_c75_m3a3_rows.py` - the verified read-only pattern this file is cut from (phase_0 pins,
    phase_1 restart+scratch, phase_hygiene, gate/fact format, the deadline reserve). Run: 6/0, rc=0, 147 s.
  * `tools/bench/diag_c75b_loopterms.py` - the terminal-table-on-the-owning-node route, 5/0, rc=0, 4 s.
  * `tools/recipes/build_opfstunnelterm_v2.py:745` `read_tunnel` - the ONLY caller shape for the two tunnel
    ops; reused verbatim with the archived labels `tools/bench/opfsinnertunnelterm_labels.json`.
  * `tools/recipes/build_d1_m3a1.py` - `find_node`:541, `terms_at`:500, `term_state`:524 (imported).
  * `tools/recipes/build_d1_v0.py` - `owner_of`:338, `diag_index`:357.
  * `tools/gscript.py` - `report_all`:502, `node_labels`:601, `node_terms_uid`:955, `uids`:1047,
    `ensure_loaded`:1298, `exec_state`:2007, `ref_counts`:233, `op`:210.
NOTHING NEW IS BUILT (user, 2026-09-18 08:53 "장치는 더 만들지 말고 계속 진행").

PREDICTION CONTRACT (hygiene gates ONLY; these are the only things that can FAIL):
  H1  the bed's md5 is `33ef524e0b6b193a158c9221474c68e3` BEFORE the run.
  H2  the bed's md5 is unchanged AFTER the run.
  H3  the five md5 pins (ORIGINAL, S1, S2, the row-2 bed, the M3a-2 artefact) all hold after the run.
  H4  the scratch copy is deleted and no longer on disk.
  H5  gscript's in-process VI-Server reference counter is level (opened == closed) at exit.
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
from build_d1_m3a1 import find_node, terms_at, term_state                         # noqa: E402
from build_opfstunnelterm_v2 import read_tunnel                                   # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3_20260922_081056.vi")
BED_MD5 = "33ef524e0b6b193a158c9221474c68e3"
M3A2 = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi")
M3A2_MD5 = "3842f5e6f128226235dc78353f26ef44"
ROW2 = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
ROW2_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
S2 = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2, S2_MD5), ("ROW2 bed", ROW2, ROW2_MD5), ("M3a-2", M3A2, M3A2_MD5))

OP_IN = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
LABELS_IN = os.path.join(BENCH, "opfsinnertunnelterm_labels.json")

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C77SCRATCH_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c77_rowd_addr.json")

TUNNEL = 7468                 # the row-D sink, a FlatSequenceInnerTunnel
FS_OWNER = 681                # its owner per diag_c75_m3a3_rows.log:163
FS_NESTED = 43914             # FlatSequence, owner column 'Diagram'
FS_TOP = 12938                # FlatSequence, owner column 'TopLevelDiagram'
WIRE_D = 7506                 # the wire row D would delete
D686 = 686                    # the diagram Pre-decided 104 addresses row C on
D686_IDX = 19                 # its traverse index, measured at diag_c75b_loopterms.log:73
NODE_CAP = 300
RUN_DEADLINE_S = 22 * 60.0
RESERVE_S = 170.0

T0 = time.time()
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "scratch": SCRATCH, "bed": BED,
     "A": {}, "B": {}, "C": {}, "D": {}, "E": {}, "H": {}}
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


# ================================================================== [0] files only, zero LabVIEW
def phase_0():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, and the five pins")
    got = md5(BED)
    R["bed_md5_before"] = got
    R["bed_bytes"] = os.path.getsize(BED)
    gate("H1 bed md5 before == %s" % BED_MD5, got == BED_MD5,
         "got %s, %d bytes" % (got, R["bed_bytes"]))
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))


# ================================================================== [1] restart + the scratch copy
def phase_1():
    head("[1] RESTART LabVIEW (STATUS NEXT orders it before the first batch), then the scratch copy")
    before, _ = safe("handles before restart", labview_handles)
    R["H"]["handles_before_restart"] = before
    fact("LabVIEW handle count BEFORE the restart: %r (baseline ~31,500)" % before)
    _, err = safe("restart_labview", restart_labview)
    R["H"]["restart_error"] = err
    g.reset()
    time.sleep(3.0)
    after, _ = safe("handles after restart", labview_handles)
    R["H"]["handles_after_restart"] = after
    fact("LabVIEW handle count AFTER the restart: %r (baseline ~31,500)" % after)
    shutil.copyfile(BED, SCRATCH)
    time.sleep(0.4)
    R["scratch_md5"] = md5(SCRATCH)
    fact("scratch %s md5 %s (copy of the bed, %d bytes)"
         % (os.path.basename(SCRATCH), R["scratch_md5"], os.path.getsize(SCRATCH)))
    t = time.time()
    _, err = safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("ensure_loaded(scratch) took %.1f s%s" % (time.time() - t, ((" ERROR " + err) if err else "")))
    es, _ = safe("exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state_cold"] = es
    fact("ExecState of the scratch (= the bed) = %r - RECORDED ONLY, never a discriminator here "
         "(Pre-decided 95, 42(c))" % es)


# ================================================================== [A] the op on 7468
def phase_a():
    head("[A] OpFsInnerTunnelTerm_v0 on uid %d - the read the c76b review calls addressable today" % TUNNEL)
    if not os.path.isfile(OP_IN):
        fact("A OP NOT ON DISK: %s - phase A cannot run (the same class of defect run 1 hit with "
             "OpConnectNested_v2.vi)" % OP_IN)
        R["A"]["op_on_disk"] = False
        return
    R["A"]["op_on_disk"] = True
    fact("A op on disk: %s (%d bytes)" % (OP_IN, os.path.getsize(OP_IN)))
    labs, err = safe("A load labels", lambda: json.load(open(LABELS_IN, encoding="utf-8")), None)
    if not labs:
        R["A"]["labels_error"] = err
        return
    R["A"]["labels_file"] = LABELS_IN
    vi, err = safe("A g.op(OP_IN)", lambda: g.op(OP_IN))
    if vi is None:
        R["A"]["op_ref_error"] = err
        return
    rd, err = safe("A read_tunnel(#%d)" % TUNNEL, lambda: read_tunnel(vi, labs, SCRATCH, TUNNEL))
    R["A"]["read_7468"] = rd
    R["A"]["read_7468_error"] = err
    if rd:
        fact("A RAW RETURN for #%d: %s" % (TUNNEL, json.dumps(rd, default=str)[:700]))
        fact("A #%d self class echo %r uid echo %r ; cast %r" % (TUNNEL, rd.get("cls_back"),
                                                                 rd.get("uid_back"), rd.get("cast_class")))
        fact("A #%d %s terminal #%r wire #%r ; %s terminal #%r wire #%r ; is_source %r ; owner %r#%r"
             % (TUNNEL, labs.get("face_a"), rd.get("term_a_uid"), rd.get("wire_a"), labs.get("face_b"),
                rd.get("term_b_uid"), rd.get("wire_b"), rd.get("is_source"), rd.get("ownercls"),
                rd.get("owner_uid")))
        fact("A #%d ERROR COLUMNS VERBATIM: err=%r err_a=%r err_b=%r errs=%r"
             % (TUNNEL, rd.get("err"), rd.get("err_a"), rd.get("err_b"), rd.get("errs")))
        got_term = bool(rd.get("term_a_uid")) and not rd.get("err_a")
        R["A"]["returned_a_terminal_reference"] = got_term
        fact("A VERDICT (measurement, not a gate): the op %s a terminal reference for #%d"
             % (("RETURNED" if got_term else "DID NOT RETURN"), TUNNEL))
        carries = [k for k, w in (("%s" % labs.get("face_a"), rd.get("wire_a")),
                                  ("%s" % labs.get("face_b"), rd.get("wire_b"))) if w == WIRE_D]
        R["A"]["faces_carrying_wire_7506"] = carries
        fact("A which face of #%d carries wire %d: %r" % (TUNNEL, WIRE_D, carries))
    # the CONTROL read: another FlatSequenceInnerTunnel of the SAME target
    fsits, err = safe("A uids('FlatSequenceInnerTunnel')",
                      lambda: sorted(g.uids(SCRATCH, "FlatSequenceInnerTunnel")), [])
    R["A"]["fsit_count"] = len(fsits or [])
    R["A"]["fsit_first"] = (fsits or [])[:6]
    fact("A FlatSequenceInnerTunnel census on the scratch: %d uid(s); first %r ; is #%d among them? %r"
         % (len(fsits or []), (fsits or [])[:6], TUNNEL, TUNNEL in (fsits or [])))
    ctrl_uid = next((u for u in (fsits or []) if u != TUNNEL), None)
    if ctrl_uid is None:
        fact("A no OTHER FlatSequenceInnerTunnel exists to use as a control read")
        return
    crd, cerr = safe("A control read_tunnel(#%r)" % ctrl_uid,
                     lambda: read_tunnel(vi, labs, SCRATCH, ctrl_uid))
    R["A"]["control_read"] = {"uid": ctrl_uid, "read": crd, "error": cerr}
    if crd:
        fact("A CONTROL #%r: %s #%r wire #%r | %s #%r wire #%r | err_a=%r errs=%r -> the op %s on THIS "
             "target" % (ctrl_uid, labs.get("face_a"), crd.get("term_a_uid"), crd.get("wire_a"),
                         labs.get("face_b"), crd.get("term_b_uid"), crd.get("wire_b"), crd.get("err_a"),
                         crd.get("errs"), ("WORKS" if crd.get("term_a_uid") else "FAILS TOO")))


# ================================================================== [B] find_node on the three uids
def phase_b():
    head("[B] find_node on #%d (nested FS), #%d (top-level FS) and #%d (the owner) - the class/owner/"
         "specific separator" % (FS_NESTED, FS_TOP, FS_OWNER))
    R["B"]["rows"] = {}
    for label, uid in (("FlatSequence NESTED #%d" % FS_NESTED, FS_NESTED),
                       ("FlatSequence TOP-LEVEL #%d" % FS_TOP, FS_TOP),
                       ("FlatSequence OWNER #%d" % FS_OWNER, FS_OWNER)):
        if left_s() < 120:
            fact("B %s: deadline reserve reached before the sweep - reported, not guessed" % label)
            continue
        loc = find_node(SCRATCH, uid, [D686_IDX, 0], "B %s" % label, budget_s=min(200.0, left_s()),
                        quiet=True)
        f = loc.get("found") or {}
        R["B"]["rows"][uid] = {"found": f, "diagram_rows": loc.get("diagram_rows"),
                               "scanned_count": len(loc.get("scanned", [])),
                               "scanned": loc.get("scanned", []),
                               "scan_cost_s": loc.get("scan_cost_s"),
                               "scan_stopped": loc.get("scan_stopped"),
                               "census_error": loc.get("diagram_census_error")}
        fact("B %s -> found %r ; %d of %d diagram(s) scanned in %.1fs ; stopped %r ; census error %r"
             % (label, (f or None), len(loc.get("scanned", [])), loc.get("diagram_rows"),
                loc.get("scan_cost_s") or 0.0, loc.get("scan_stopped"), loc.get("diagram_census_error")))
        errs = [s for s in loc.get("scanned", []) if s.get("error")]
        R["B"]["rows"][uid]["scanned_with_errors"] = len(errs)
        fact("B %s per-diagram scan rows KEPT: %d with a node_labels ERROR, total nodes seen %d "
             "(run 2 discarded exactly this dataset - c76b process note)"
             % (label, len(errs), sum(int(s.get("nodes") or 0) for s in loc.get("scanned", []))))
        for s in errs[:5]:
            fact("    B %s scan ERROR at Diagram idx %r (#%r): %s"
                 % (label, s.get("diagram_index"), s.get("diagram_uid"), (s.get("error") or "")[:140]))
    # the class-level question, answered from the census rather than by inference
    rows, err = safe("B report_all('FlatSequence')", lambda: g.report_all(SCRATCH, "FlatSequence"), [])
    R["B"]["flatsequence_census"] = rows
    fact("B FlatSequence census: %d row(s)%s" % (len(rows or []), ((" ERROR " + err) if err else "")))
    for r in (rows or []):
        fact("    B FlatSequence i=%r uid=%r class=%r owner=%r" % (r.get("i"), r.get("uid"),
                                                                   r.get("class"), r.get("owner")))
    (ocls, ouid), oerr = safe("B owner_of(#%d)" % FS_OWNER, lambda: owner_of(SCRATCH, FS_OWNER),
                              (None, None))
    R["B"]["owner_of_681"] = {"class": ocls, "uid": ouid, "error": oerr}
    fact("B owner_of(#%d) = %r #%r%s (THIS is the call run 2's brief quoted as #681 while the recipe "
         "had actually called it on #686 - c76b finding 1)"
         % (FS_OWNER, ocls, ouid, ((" ERROR " + oerr) if oerr else "")))
    di, _ = safe("B diag_index(#%d)" % FS_OWNER, lambda: diag_index(SCRATCH, FS_OWNER), None)
    R["B"]["diag_index_681"] = di
    fact("B diag_index(#%d) = %r (a Diagram-census index; None/raise = #%d is NOT a diagram)"
         % (FS_OWNER, di, FS_OWNER))


# ================================================================== [C] the Diagram census head
def phase_c():
    head("[C] report_all(TARGET,'Diagram') rows 0-3 - is row 0 still TopLevelDiagram #536")
    rows, err = safe("C report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    R["C"]["diagram_rows"] = len(rows or [])
    R["C"]["head"] = (rows or [])[:4]
    R["C"]["error"] = err
    fact("C Diagram census: %d row(s)%s" % (len(rows or []), ((" ERROR " + err) if err else "")))
    for r in (rows or [])[:4]:
        fact("    C Diagram[%r] uid=%r class=%r owner=%r" % (r.get("i"), r.get("uid"), r.get("class"),
                                                             r.get("owner")))
    r0 = (rows or [{}])[0] if rows else {}
    R["C"]["row0_is_toplevel_536"] = (r0.get("class") == "TopLevelDiagram" and r0.get("uid") == 536)
    fact("C row 0 is TopLevelDiagram #536? %r (measured %r #%r)"
         % (R["C"]["row0_is_toplevel_536"], r0.get("class"), r0.get("uid")))
    idx686 = next((r["i"] for r in (rows or []) if r["uid"] == D686), None)
    R["C"]["d686_index"] = idx686
    fact("C Diagram #%d sits at traverse index %r (Pre-decided 104 addresses row C at idx %d)"
         % (D686, idx686, D686_IDX))


# ================================================================== [D] the owning node's terminal table
def phase_d():
    head("[D] Pre-decided 107: the terminal table of the OWNING NODE FlatSequence #%d on Diagram #%d "
         "(traverse idx %d)" % (FS_OWNER, D686, D686_IDX))
    idx = R["C"].get("d686_index")
    if idx is None:
        fact("D Diagram #%d was not in the census - using the planned traverse index %d, LABELLED as "
             "unverified" % (D686, D686_IDX))
        idx = D686_IDX
    R["D"]["diagram_index_used"] = idx
    labels, lerr = safe("D node_labels(%r)" % idx, lambda: g.node_labels(SCRATCH, idx), [])
    R["D"]["nodes_on_d686"] = len(labels or [])
    R["D"]["node_labels_error"] = lerr
    fact("D Diagram #%d Nodes[]: %d row(s)%s" % (D686, len(labels or []),
                                                 ((" ERROR " + lerr) if lerr else "")))
    hit = next((k for k, r in enumerate(labels or []) if r.get("uid") == FS_OWNER), None)
    R["D"]["nodes_index_of_681"] = hit
    fact("D is FlatSequence #%d a member of Diagram #%d's Nodes[]? %s"
         % (FS_OWNER, D686, ("YES at Nodes[%d]" % hit) if hit is not None else "NO - absent from the list"))
    if hit is not None:
        tt = terms_at(SCRATCH, idx, hit, FS_OWNER, "D FlatSequence #%d" % FS_OWNER, quiet=True)
        R["D"]["terminal_table"] = tt
        rows = tt.get("terminals", [])
        fact("D FlatSequence #%d TERMINAL TABLE (uid echo %r): %d entr(y/ies)%s"
             % (FS_OWNER, tt.get("uid_echo"), len(rows),
                (("  READ ERROR " + tt["error_verbatim"]) if tt.get("error_verbatim") else "")))
        for t in rows:
            fact("    D #%d t%-3d name=%-30r is_source=%-5r wire=%-8r state=%s"
                 % (FS_OWNER, t["i"], t["name"], t["is_source"], t["wire"], term_state(t)))
        carry = [t for t in rows if t.get("wire") == WIRE_D]
        R["D"]["entries_carrying_7506"] = carry
        R["D"]["count_carrying_7506"] = len(carry)
        fact("D *** ENTRIES OF #%d's TERMINAL TABLE CARRYING CONNECTED WIRE %d: %d (%s) *** %r"
             % (FS_OWNER, WIRE_D, len(carry),
                {0: "ZERO", 1: "EXACTLY ONE"}.get(len(carry), "MORE THAN ONE"),
                [(t["i"], t["name"], t["is_source"]) for t in carry]))
        return
    R["D"]["count_carrying_7506"] = None
    fact("D *** #%d HAS NO Nodes[] TERMINAL TABLE ON THIS PATH, so the count of entries carrying wire "
         "%d is NOT ZERO AND NOT ONE - IT IS UNREADABLE BY THIS ROUTE ***" % (FS_OWNER, WIRE_D))
    # LABELLED SECONDARY: which terminals of diagram #686 DO carry wire 7506
    head("[D2] LABELLED SECONDARY - every OTHER node of Diagram #%d, which terminals carry wire %d"
         % (D686, WIRE_D))
    cls_by_uid = {}
    nrows, _ = safe("D2 report_all('Node')", lambda: g.report_all(SCRATCH, "Node"), [])
    for o in (nrows or []):
        cls_by_uid[o["uid"]] = o["class"]
    R["D"]["node_class_map"] = len(cls_by_uid)
    fact("D2 Node class map: %d entries" % len(cls_by_uid))
    n_max = min(len(labels or []), NODE_CAP)
    found, scanned, errors = [], 0, []
    for n in range(n_max):
        if left_s() < 90:
            R["D"]["secondary_truncated"] = "deadline reserve reached after %d node(s)" % scanned
            fact("D2 %s - census TRUNCATED, reported not guessed" % R["D"]["secondary_truncated"])
            break
        scanned += 1
        try:
            node_uid, trows = g.node_terms_uid(SCRATCH, idx, n)
        except Exception as e:                                                    # noqa: BLE001
            errors.append({"n": n, "error": str(e)[:160]})
            continue
        if not node_uid:
            break
        for t in trows:
            if t.get("wire") == WIRE_D:
                found.append({"nodes_index": n, "node_uid": node_uid,
                              "node_class": cls_by_uid.get(node_uid),
                              "node_label": (labels[n].get("label") if n < len(labels or []) else None),
                              "terminal_index": t["i"], "terminal_name": t["name"],
                              "is_source": t["is_source"]})
    R["D"]["secondary_scanned"] = scanned
    R["D"]["secondary_errors"] = errors
    R["D"]["secondary_hits_7506"] = found
    fact("D2 scanned %d of %d node(s) of Diagram #%d ; %d read error(s) ; %d terminal(s) carry wire %d"
         % (scanned, len(labels or []), D686, len(errors), len(found), WIRE_D))
    for h in found:
        fact("    D2 wire %d <- Nodes[%d] #%r %r label=%r t%d name=%r is_source=%r"
             % (WIRE_D, h["nodes_index"], h["node_uid"], h["node_class"], h["node_label"],
                h["terminal_index"], h["terminal_name"], h["is_source"]))
    for e in errors[:5]:
        fact("    D2 node_terms_uid(%d, %d) ERROR: %s" % (idx, e["n"], e["error"]))


# ================================================================== [E] cited, not re-measured
def phase_e():
    head("[E] CITED, NOT RE-MEASURED (Pre-decided 108) - the same read on the owning LOOP node")
    for line in ("tools/bench/diag_c75b_loopterms.log:73  NEW WhileLoop #23032 LIVE LOOKUP: Diagram #686 "
                 "(traverse index 19), Nodes[21], label 'While Loop'",
                 "tools/bench/diag_c75b_loopterms.log:74  NEW WhileLoop #23032 BORDER TERMINAL TABLE "
                 "(uid echo 23032): 7 terminal(s) - this is the table a (diagram, node, terminal) verb "
                 "addresses",
                 "tools/bench/diag_c75b_loopterms.log:76  t1 name='Outgoing Handle' is_source=True "
                 "wire=0 state=BARE  <- row D's NEW SOURCE #23868 RIGHT OUTER",
                 "tools/bench/diag_c75b_loopterms.log:82  NEW WhileLoop #23032 BARE terminal indices: "
                 "[(1, 'Outgoing Handle', True), (3, 'Out position', True)]",
                 "tools/bench/diag_c75b_loopterms.log:21  OLD WhileLoop #637 t10 name='Outgoing Handle' "
                 "is_source=True wire=7506 state=WIRED  <- the wire row D deletes, on the OLD loop"):
        fact("E %s" % line)
    R["E"]["cited"] = "tools/bench/diag_c75b_loopterms.log:21,73,74,76,82"


# ================================================================== [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close the scratch, delete it, re-read every pin, handles at both ends")
    safe("close_panel(scratch)", lambda: g.close_panel(SCRATCH))
    R["H"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts (opened / closed / live / cached op VIs): %r" % R["H"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         R["H"]["ref_counts"]["live"] == 0, "%r" % R["H"]["ref_counts"])
    handles, _ = safe("handles after", labview_handles)
    R["H"]["handles_after_reads"] = handles
    fact("LabVIEW handle count AFTER the reads: %r (after the restart it was %r ; baseline ~31,500)"
         % (handles, R["H"].get("handles_after_restart")))
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
    got = md5(BED)
    R["bed_md5_after"] = got
    gate("H2 bed md5 UNCHANGED after the run", got == R.get("bed_md5_before"),
         "before %s / after %s" % (R.get("bed_md5_before"), got))
    allpins = True
    R["pins_after"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_after"][label] = have
        allpins = allpins and (have == want)
        fact("PIN AFTER  %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the five md5 pins all hold", allpins)
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c77_rowd_addr - MEASUREMENT ONLY, hygiene gates only (Pre-decided 63)", flush=True)
    print("=" * 100, flush=True)
    try:
        phase_0()
        phase_1()
        phase_a()
        phase_b()
        phase_c()
        phase_d()
        phase_e()
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
          % (len(passes), len(fails), (("  FAILING: " + ", ".join(fails)) if fails else "")), flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
