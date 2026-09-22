"""DIAGNOSTIC, MEASUREMENT ONLY - D-1 of M3a-3b (`docs/cycle27-plan.md` Pre-decided 121 + 122).

THE ONE QUESTION: does `UID to GObject Reference.vi` resolve a **TERMINAL** uid? It is proven today only on
TUNNEL uids (`OpFsInnerTunnelTerm_v0` on #7468) and WIRE uids (`OpWireSource_v5` on w7506).

WHAT THIS IS NOT: it builds nothing, creates no op, edits nothing, saves nothing, runs no deliverable VI, and
touches no motor / ASI / camera (rig state 조립). It COPIES the bed to a dated scratch name, READS the scratch,
deletes the scratch in the same run and re-reads every md5 pin. Per Pre-decided 63 a measurement-only diagnostic
GATES ON HYGIENE ONLY: a negative measurement is a FACT line, never a failing gate. A REFUSED call is a RESULT.
`ExecState` is recorded once as a FACT and is NEVER a discriminator (the bed is BROKEN BY DESIGN, Pre-decided 95).

PRIOR ART CHECKED BEFORE WRITING A LINE (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/diag_c77_rowd_addr.py` - the verified read-only skeleton this file is cut from (phase_0 pins,
    phase_1 restart+scratch, phase_hygiene, gate/fact format, deadline reserve). Ran 5/0, rc=0, 144 s.
  * `tools/recipes/build_opfstunnelterm_v2.py:745 read_tunnel` - the ONLY caller shape for the FSIT ops; it
    already POISONS `cls_back`/`uid_back`/`cast_class` before the run (the cycle-68 history-echo repair).
  * `tools/recipes/build_opownerchain_v1.py:246 read_owner` + `tools/recipes/build_d1_v0.py:338 owner_of` -
    the uid -> owner reader. `OpOwnerChain_v1` IS `UID to GObject Reference.vi` -> `Generic.Owner` -> ClassName
    + TMSC(GObject) -> UID, with a SELF class/uid echo: that echo is exactly this dispatch's measurement.
    ⚠️ `read_owner` does NOT poison `cls_back`/`uid_back`; this file re-implements the drive and DOES, so the
    uid echo is an anti-history-echo check and not a stale readout.
  * `tools/recipes/build_opwiresource_v5.py:155 read_terminal` - the wire-uid control; measured to return the
    OWNER of each `Wire.Terms[]` entry but NOT the terminal's own uid, so it cannot re-derive TARGET B.
  * `tools/gscript.py` - `report_all`:502, `node_terms_uid`:955, `subvis`:539, `shift_reg`:783, `uids`:1047,
    `ensure_loaded`:1298, `exec_state`:2007, `ref_counts`:233, `op`:210, `_err`:449.
  * label maps surveyed for a `Terminal`-seeded TMSC: `tools/bench/*labels*.json`. The only class-seeded casts
    on disk are `VI Server:FlatSequenceInnerTunnel` (opfsinnertunnelterm), `VI Server:FlatSequenceOuterTunnel`
    (opfstunnelterm), `Wire` (opwiresource_v5 seedW) and `GObject` (opwiresource_v5 seedG). NO OP ON DISK
    CARRIES A `Terminal`-SEEDED `To More Specific Class`, so the literal "TMSC -> Terminal" column cannot be
    measured without BUILDING, which this dispatch forbids. It is therefore measured in the two forms that DO
    exist, and the gap is stated as a fact:
      (i)  TMSC -> GObject   on the same reference (`OpOwnerChain_v1` seedG, label `cast_class`)
      (ii) TMSC -> FlatSequenceInnerTunnel on the same reference (`OpFsInnerTunnelTerm_v0`, label `cast_class`)
           - a DELIBERATE class mismatch on a terminal uid, whose raw error code calibrates what a TMSC refusal
           looks like on this path.
NOTHING NEW IS BUILT (user, 2026-09-18 08:53 "장치는 더 만들지 말고 계속 진행").

MEASUREMENT PLAN
  [V] LabVIEW version / application directory / bitness, and the ON-DISK PATH of the
      `UID to GObject Reference.vi` actually called (read from each probing op's own SubVIs[]).
  [A] RE-DERIVE TARGET A: `OpFsInnerTunnelTerm_v0` on `FlatSequenceInnerTunnel #7468` -> its LEFT terminal's own
      UID. Expected #7488; whatever comes back is reported.
  [B] RE-DERIVE TARGET B: `WhileLoop #23032` `Nodes[21]` terminal 1 ('Outgoing Handle'), the row-D source, and
      its OWNER (Pre-decided 120 expects `RightShiftRegister #23868`, NOT the loop). The terminal's own UID has
      no reader on disk for a BARE shift-register outer terminal, so it is sought by a `Terminal` Traverse
      census + owner resolution; if the Traverse does not return terminals that is reported as the finding.
  [P] THE PROBE, identical columns for every uid: raw error cluster, returned `Class Name`, TMSC result, uid
      echo. Targets A and B; CONTROLS = `FlatSequenceInnerTunnel #7468` (proven tunnel uid) and wire #7506
      (proven wire uid), so a NO on a terminal is distinguishable from a broken harness.

PREDICTION CONTRACT (hygiene gates ONLY; these are the only things that can FAIL):
  H1 the bed's md5 is `33ef524e0b6b193a158c9221474c68e3` BEFORE the run.
  H2 the bed's md5 is unchanged AFTER the run.
  H3 the five md5 pins (ORIGINAL, S1, S2, the row-2 bed, the M3a-2 artefact) all hold after the run.
  H4 the scratch copy is deleted and no longer on disk.
  H5 gscript's in-process VI-Server reference counter is level (opened == closed) at exit.
  H6 the run left NO file on disk other than this log and its JSON sidecar.
"""
import glob
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

OP_FSIT = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
LAB_FSIT = os.path.join(BENCH, "opfsinnertunnelterm_labels.json")
OP_OWNER = os.path.join(g.CLAUDEDEV, "OpOwnerChain_v1.vi")
LAB_OWNER = os.path.join(BENCH, "opwiresource_v5_labels.json")

FSIT_UID = 7468          # CONTROL 1: a proven tunnel uid (Pre-decided 109)
WIRE_UID = 7506          # CONTROL 2: a proven wire uid (the live net on the bed)
TERM_A_EXPECT = 7488     # what STATUS says the FSIT LEFT terminal is; RE-DERIVED, never assumed
LOOP_NEW = 23032         # the NEW WhileLoop; its Nodes[] index on Diagram #686
LOOP_NODES_IDX = 21
LOOP_TERM_IDX = 1        # 'Outgoing Handle' - row D's SOURCE, BARE on the bed
RSR_EXPECT = 23868       # Pre-decided 120: the OWNER of that terminal is the register, not the loop
D686 = 686
D686_IDX = 19
TERMCENSUS_OWNERS_CAP = 60

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "C81SCRATCH_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c81_uidref.json")

RUN_DEADLINE_S = 20 * 60.0
RESERVE_S = 180.0

T0 = time.time()
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "scratch": SCRATCH, "bed": BED,
     "V": {}, "A": {}, "B": {}, "P": {}, "S": {}, "H": {}}
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
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the five pins, and the claudeDev file list")
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
    R["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))


# ================================================================== [1] restart + the scratch copy
def phase_1():
    head("[1] RESTART LabVIEW (STATUS NEXT orders it - left at ~31,281 handles), then the scratch copy")
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
    gate("H0 the scratch is a byte-identical copy of the bed", R["scratch_md5"] == R["bed_md5_before"],
         "%s vs %s" % (R["scratch_md5"], R["bed_md5_before"]))
    fact("scratch %s md5 %s (%d bytes)"
         % (os.path.basename(SCRATCH), R["scratch_md5"], os.path.getsize(SCRATCH)))
    t = time.time()
    _, err = safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(SCRATCH))
    fact("ensure_loaded(scratch) took %.1f s%s" % (time.time() - t, ((" ERROR " + err) if err else "")))
    es, _ = safe("exec_state(scratch)", lambda: g.exec_state(SCRATCH))
    R["exec_state_cold"] = es
    fact("ExecState of the scratch (= the bed) = %r - RECORDED ONLY, never a discriminator (Pre-decided 95)" % es)


# ================================================================== [V] attribution
def phase_v():
    head("[V] ATTRIBUTION - LabVIEW version/bitness and the ON-DISK PATH of the UID-to-GObject VI called")
    app, _ = safe("g.lv()", g.lv)
    for prop in ("Version", "ApplicationDirectory", "Name"):
        val, e = safe("Application.%s" % prop, lambda p=prop: getattr(app, p))
        R["V"][prop] = val
        fact("LabVIEW Application.%-20s = %r%s" % (prop, val, ((" ERROR " + e) if e else "")))
    appdir = R["V"].get("ApplicationDirectory") or ""
    R["V"]["bitness_guess"] = ("32-bit (Program Files (x86))" if "(x86)" in str(appdir)
                               else "64-bit (not under Program Files (x86))")
    fact("bitness read from the application directory: %s" % R["V"]["bitness_guess"])
    R["V"]["python"] = "%d.%d.%d %s" % (sys.version_info[:3] + (("64-bit" if sys.maxsize > 2 ** 32 else "32-bit"),))
    fact("this COM client: python %s" % R["V"]["python"])
    # the path of UID to GObject Reference.vi, read from each probing op's own SubVIs[] - not from a doc
    R["V"]["uidvi_paths"] = {}
    for name, opath in (("OpOwnerChain_v1", OP_OWNER), ("OpFsInnerTunnelTerm_v0", OP_FSIT)):
        if not os.path.isfile(opath):
            fact("V %s IS NOT ON DISK: %s" % (name, opath))
            R["V"]["uidvi_paths"][name] = "OP NOT ON DISK"
            continue
        rows, e = safe("V subvis(%s)" % name, lambda p=opath: g.subvis(p, 0), [])
        hits = [r for r in (rows or []) if "uid to gobject" in str(r.get("name", "")).lower()]
        R["V"]["uidvi_paths"][name] = {"subvi_rows": len(rows or []), "hits": hits, "error": e}
        fact("V %s SubVIs[] on diagram 0: %d row(s)%s" % (name, len(rows or []), ((" ERROR " + e) if e else "")))
        for h in hits:
            fact("    V %s CALLS %r  uid #%r  PATH %r" % (name, h.get("name"), h.get("uid"), h.get("path")))
        if not hits:
            fact("    V %s: no SubVIs[] row whose name contains 'UID to GObject' on diagram 0 "
                 "(it may sit on an inner diagram - reported, not inferred)" % name)
    guess = os.path.join(str(R["V"].get("ApplicationDirectory") or ""), "vi.lib", "VIServer",
                         "UID to GObject Reference.vi")
    R["V"]["uidvi_expected_path"] = guess
    R["V"]["uidvi_expected_exists"] = os.path.isfile(guess)
    fact("V the documented location %r exists on disk? %r" % (guess, R["V"]["uidvi_expected_exists"]))


# ================================================================== [A] re-derive TARGET A
def phase_a():
    head("[A] RE-DERIVE TARGET A - OpFsInnerTunnelTerm_v0 on FlatSequenceInnerTunnel #%d -> its LEFT terminal uid"
         % FSIT_UID)
    if not os.path.isfile(OP_FSIT):
        fact("A OP NOT ON DISK: %s - TARGET A cannot be re-derived" % OP_FSIT)
        R["A"]["op_on_disk"] = False
        return
    R["A"]["op_on_disk"] = True
    labs, e = safe("A load labels", lambda: json.load(open(LAB_FSIT, encoding="utf-8")), None)
    if not labs:
        R["A"]["labels_error"] = e
        return
    R["A"]["labels"] = LAB_FSIT
    vi, e = safe("A g.op(OP_FSIT)", lambda: g.op(OP_FSIT))
    if vi is None:
        R["A"]["op_ref_error"] = e
        return
    rd, e = safe("A read_tunnel(#%d)" % FSIT_UID, lambda: read_tunnel(vi, labs, SCRATCH, FSIT_UID))
    R["A"]["read"] = rd
    R["A"]["read_error"] = e
    if not rd:
        return
    fact("A RAW RETURN for #%d: %s" % (FSIT_UID, json.dumps(rd, default=str)[:600]))
    fact("A #%d self echo %r#%r ; cast(FlatSequenceInnerTunnel) -> %r ; owner %r#%r"
         % (FSIT_UID, rd.get("cls_back"), rd.get("uid_back"), rd.get("cast_class"),
            rd.get("ownercls"), rd.get("owner_uid")))
    fact("A #%d %s terminal #%r wire #%r | %s terminal #%r wire #%r"
         % (FSIT_UID, labs.get("face_a"), rd.get("term_a_uid"), rd.get("wire_a"),
            labs.get("face_b"), rd.get("term_b_uid"), rd.get("wire_b")))
    fact("A #%d ERROR COLUMNS VERBATIM: err=%r err_a=%r err_b=%r errs=%r"
         % (FSIT_UID, rd.get("err"), rd.get("err_a"), rd.get("err_b"), rd.get("errs")))
    R["A"]["target_a_uid"] = rd.get("term_a_uid")
    R["A"]["matches_status_7488"] = (rd.get("term_a_uid") == TERM_A_EXPECT)
    fact("A *** TARGET A (the FSIT #%d LEFT terminal) RE-DERIVED AS #%r ; STATUS said #%d -> %s ***"
         % (FSIT_UID, rd.get("term_a_uid"), TERM_A_EXPECT,
            ("SAME" if R["A"]["matches_status_7488"] else "DIFFERENT - the re-derived value is what is probed")))


# ================================================================== [B] re-derive TARGET B
def phase_b():
    head("[B] RE-DERIVE TARGET B - WhileLoop #%d Nodes[%d] terminal %d, and its OWNER"
         % (LOOP_NEW, LOOP_NODES_IDX, LOOP_TERM_IDX))
    rows, e = safe("B report_all('Diagram')", lambda: g.report_all(SCRATCH, "Diagram"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == D686), None)
    R["B"]["d686_index"] = idx
    fact("B Diagram census: %d row(s) ; Diagram #%d sits at traverse index %r (planned %d)%s"
         % (len(rows or []), D686, idx, D686_IDX, ((" ERROR " + e) if e else "")))
    if idx is None:
        idx = D686_IDX
        fact("B using the planned traverse index %d, LABELLED unverified" % idx)
    echo, trows = (None, [])
    (echo, trows), e = safe("B node_terms_uid(%r, %d)" % (idx, LOOP_NODES_IDX),
                            lambda: g.node_terms_uid(SCRATCH, idx, LOOP_NODES_IDX), (None, []))
    R["B"]["loop_uid_echo"] = echo
    R["B"]["loop_terms"] = trows
    R["B"]["loop_terms_error"] = e
    fact("B Nodes[%d] of Diagram #%d: node uid echo %r (expected the NEW WhileLoop #%d -> %s), %d terminal(s)"
         % (LOOP_NODES_IDX, D686, echo, LOOP_NEW, ("MATCH" if echo == LOOP_NEW else "MISMATCH"), len(trows or [])))
    for t in (trows or []):
        fact("    B #%r t%-2d name=%-22r is_source=%-5r wire=%-7r errs=%r"
             % (echo, t["i"], t["name"], t["is_source"], t["wire"],
                [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]))
    trow = next((t for t in (trows or []) if t["i"] == LOOP_TERM_IDX), None)
    R["B"]["target_row"] = trow
    fact("B TARGET B's ROW: %r" % (trow,))
    # the RightShiftRegister census - is #23868 there at all, and what does the loop own
    rsr, e = safe("B report_all('RightShiftRegister')",
                  lambda: g.report_all(SCRATCH, "RightShiftRegister"), [])
    R["B"]["rsr_count"] = len(rsr or [])
    R["B"]["rsr_has_expect"] = any(r["uid"] == RSR_EXPECT for r in (rsr or []))
    fact("B RightShiftRegister census: %d row(s) ; is #%d among them? %r%s"
         % (len(rsr or []), RSR_EXPECT, R["B"]["rsr_has_expect"], ((" ERROR " + e) if e else "")))
    # TARGET B's own terminal uid: no reader on disk returns a BARE shift-register outer terminal's uid, so
    # the ONLY route with existing ops is a Terminal Traverse census + owner resolution. Measured, not assumed.
    tcs, e = safe("B report_all('Terminal')", lambda: g.report_all(SCRATCH, "Terminal"), [])
    R["B"]["terminal_census_rows"] = len(tcs or [])
    R["B"]["terminal_census_error"] = e
    fact("B Traverse census of class 'Terminal': %d row(s)%s  <- if 0/error, a BARE terminal's own uid has NO "
         "reader on disk and TARGET B's uid is NOT DERIVABLE without building"
         % (len(tcs or []), ((" ERROR " + e) if e else "")))
    if not tcs:
        R["B"]["target_b_uid"] = None
        fact("B *** TARGET B's TERMINAL UID IS NOT DERIVABLE WITH ANY OP ON DISK - reported as the finding, "
             "not worked around ***")
        return
    cands = [r for r in tcs if str(r.get("owner")) in ("RightShiftRegister", "LeftShiftRegister")]
    R["B"]["terminal_candidates"] = len(cands)
    fact("B of those, %d row(s) report owner CLASS in (RightShiftRegister, LeftShiftRegister)" % len(cands))
    hits = []
    if os.path.isfile(OP_OWNER):
        labs = json.load(open(LAB_OWNER, encoding="utf-8"))
        vio, _ = safe("B g.op(OP_OWNER)", lambda: g.op(OP_OWNER))
        for n, r in enumerate(cands[:TERMCENSUS_OWNERS_CAP]):
            if vio is None or left_s() < 150:
                fact("B owner resolution stopped after %d candidate(s) (deadline reserve or no op ref)" % n)
                break
            o = probe_ownerchain(vio, labs, SCRATCH, r["uid"], quiet=True)
            if o.get("owner_uid") == RSR_EXPECT:
                hits.append({"terminal_uid": r["uid"], "pos": r.get("pos"), "self_class": o.get("cls_back"),
                             "owner_class": o.get("ownercls"), "owner_uid": o.get("owner_uid")})
    R["B"]["terminals_owned_by_expect"] = hits
    fact("B terminal(s) whose OWNER resolves to #%d: %d -> %r" % (RSR_EXPECT, len(hits), hits))
    R["B"]["target_b_uid"] = hits[0]["terminal_uid"] if len(hits) == 1 else None
    fact("B *** TARGET B terminal uid = %r (exactly one owned by #%d => that one; 0 or >1 => NOT DETERMINED "
         "and the probe below runs on whatever WAS determined) ***" % (R["B"]["target_b_uid"], RSR_EXPECT))


# ================================================================== the two probe drives
def probe_ownerchain(vi, lab, target, uid, quiet=False):
    """OpOwnerChain_v1 = UID to GObject Reference.vi -> [self Class Name / self UID] + Generic.Owner ->
    ClassName + TMSC(GObject seed) -> UID. EVERY readout is POISONED first (the cycle-68 anti-history-echo
    repair; `read_owner` itself poisons only three of them)."""
    for k in ("ownercls", "cls_back", "cast_class"):
        try:
            vi.SetControlValue(lab[k], "POISON")
        except Exception:
            pass
    try:
        vi.SetControlValue("Class Name 3", "POISON")
    except Exception:
        pass
    for k in ("uid_back", "owner_uid"):
        try:
            vi.SetControlValue(lab[k], 0)
        except Exception:
            pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", 0)
    vi.SetControlValue(lab["uid_in"], int(uid))
    try:
        vi.SetControlValue(lab["term_index"], 0)
    except Exception:
        pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:                                                        # noqa: BLE001
        err = "EXC %s: %s" % (type(e).__name__, str(e)[:120])
    out = {"op": "OpOwnerChain_v1", "uid_in": int(uid), "err": err}
    for k in ("cls_back", "ownercls", "cast_class"):
        out[k] = vi.GetControlValue(lab[k])
    for k in ("uid_back", "owner_uid"):
        out[k] = int(vi.GetControlValue(lab[k]))
    out["cls_482"] = vi.GetControlValue("Class Name 3")
    out["errors"] = {k: (g._err(vi, lab[k]) or "") for k in ("errL", "errT", "errO", "errU", "errG")}
    out["uid_echo_ok"] = (out["uid_back"] == int(uid))
    if not quiet:
        fact("    P[OwnerChain] uid %s -> self %r#%r (echo %s) | TMSC(GObject) -> %r | owner %r#%r | "
             "err %r | per-stage %r" % (uid, out["cls_back"], out["uid_back"],
                                        "OK" if out["uid_echo_ok"] else "MISMATCH", out["cast_class"],
                                        out["ownercls"], out["owner_uid"], out["err"],
                                        {k: v for k, v in out["errors"].items() if v}))
    return out


def probe_fsit(vi, lab, target, uid):
    """OpFsInnerTunnelTerm_v0 = the SAME UID to GObject Reference.vi, then a TMSC seeded
    `VI Server:FlatSequenceInnerTunnel`. On a TERMINAL uid that cast is a DELIBERATE class mismatch: its error
    code is what a TMSC refusal looks like on this path."""
    rd = read_tunnel(vi, lab, target, uid)
    out = {"op": "OpFsInnerTunnelTerm_v0", "uid_in": int(uid), "err": rd.get("err"),
           "cls_back": rd.get("cls_back"), "uid_back": rd.get("uid_back"),
           "cast_class": rd.get("cast_class"), "ownercls": rd.get("ownercls"),
           "owner_uid": rd.get("owner_uid"), "term_a_uid": rd.get("term_a_uid"),
           "term_b_uid": rd.get("term_b_uid")}
    out["errors"] = {k: (g._err(vi, lab[k]) or "") for k in
                     ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO", "err_a", "err_b")
                     if k in lab}
    out["uid_echo_ok"] = (out["uid_back"] == int(uid))
    fact("    P[FSIT]       uid %s -> self %r#%r (echo %s) | TMSC(FlatSequenceInnerTunnel) -> %r | "
         "err %r | per-stage %r" % (uid, out["cls_back"], out["uid_back"],
                                    "OK" if out["uid_echo_ok"] else "MISMATCH", out["cast_class"],
                                    out["err"], {k: v for k, v in out["errors"].items() if v}))
    return out


# ================================================================== [P] the probe
def phase_p():
    head("[P] THE PROBE - does UID to GObject Reference.vi resolve a TERMINAL uid? Same columns for all four")
    targets = []
    a_uid = R["A"].get("target_a_uid")
    if a_uid:
        targets.append(("TARGET A  FSIT #%d LEFT terminal" % FSIT_UID, a_uid))
    else:
        fact("P TARGET A was not re-derived - it is NOT probed (no assumed uid is ever substituted)")
    b_uid = R["B"].get("target_b_uid")
    if b_uid:
        targets.append(("TARGET B  loop #%d Nodes[%d] t%d terminal" % (LOOP_NEW, LOOP_NODES_IDX, LOOP_TERM_IDX),
                        b_uid))
    else:
        fact("P TARGET B was not re-derived - it is NOT probed (no assumed uid is ever substituted)")
    targets.append(("CONTROL 1 FlatSequenceInnerTunnel #%d (proven tunnel uid)" % FSIT_UID, FSIT_UID))
    targets.append(("CONTROL 2 wire #%d (proven wire uid)" % WIRE_UID, WIRE_UID))
    R["P"]["targets"] = [(lbl, u) for lbl, u in targets]
    labs_o = json.load(open(LAB_OWNER, encoding="utf-8")) if os.path.isfile(OP_OWNER) else None
    labs_f = json.load(open(LAB_FSIT, encoding="utf-8")) if os.path.isfile(OP_FSIT) else None
    vio, _ = safe("P g.op(OP_OWNER)", lambda: g.op(OP_OWNER)) if labs_o else (None, "")
    vif, _ = safe("P g.op(OP_FSIT)", lambda: g.op(OP_FSIT)) if labs_f else (None, "")
    R["P"]["rows"] = []
    for label, uid in targets:
        head("[P] %s  ->  uid #%s" % (label, uid))
        row = {"label": label, "uid": uid}
        if vio is not None:
            row["ownerchain"], _ = safe("P ownerchain(#%s)" % uid,
                                        lambda u=uid: probe_ownerchain(vio, labs_o, SCRATCH, u))
        if vif is not None:
            row["fsit"], _ = safe("P fsit(#%s)" % uid, lambda u=uid: probe_fsit(vif, labs_f, SCRATCH, u))
        oc = row.get("ownerchain") or {}
        fc = row.get("fsit") or {}
        row["summary"] = {
            "uid": uid,
            "returned_class_name": oc.get("cls_back"),
            "uid_echo_ok": oc.get("uid_echo_ok"),
            "uidvi_error": oc.get("errors", {}).get("errU"),
            "op_error": oc.get("err"),
            "tmsc_gobject_class": oc.get("cast_class"),
            "tmsc_gobject_error": oc.get("errors", {}).get("errG"),
            "tmsc_fsit_class": fc.get("cast_class"),
            "tmsc_fsit_error": fc.get("errors", {}).get("errCO") or fc.get("errors", {}).get("errU"),
            "owner": "%r#%r" % (oc.get("ownercls"), oc.get("owner_uid")),
        }
        fact("P SUMMARY %s: %s" % (label, json.dumps(row["summary"], default=str)))
        R["P"]["rows"].append(row)


# ================================================================== [S] the seed census
def phase_s():
    head("[S] WHY THE LITERAL 'TMSC -> Terminal' COLUMN IS NOT MEASURABLE IN THIS DISPATCH")
    seeds = {}
    for f in sorted(glob.glob(os.path.join(BENCH, "*labels*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                                         # noqa: BLE001
            continue
        if isinstance(d, dict) and d.get("class"):
            seeds[os.path.basename(f)] = d.get("class")
    R["S"]["class_seeded_label_maps"] = seeds
    fact("S class-seeded TMSC label maps on disk: %r" % seeds)
    fact("S plus the two UNNAMED seeds inside opwiresource_v5: seedW = a Wire-typed refnum, seedG = a "
         "GObject-typed refnum (docs/toolkit-capabilities.md:60-61)")
    fact("S NO op on disk carries a `Terminal`-seeded To More Specific Class, so the literal cast asked for "
         "cannot be run without BUILDING one - which this dispatch forbids (Pre-decided 122 D-1). The two "
         "casts that DO exist were run on every uid above and are reported as tmsc_gobject_* / tmsc_fsit_*.")


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
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6 THE FILES THIS RUN LEFT ON DISK: []", not added and not gone,
         "added %r removed %r" % (added, gone))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass
    print("=" * 100, flush=True)
    print("DIAGNOSTIC diag_c81_uidref - D-1 of M3a-3b, MEASUREMENT ONLY, hygiene gates only (Pre-decided 63/121)",
          flush=True)
    print("=" * 100, flush=True)
    try:
        phase_0()
        phase_1()
        phase_v()
        phase_a()
        phase_b()
        phase_p()
        phase_s()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        R["fatal"] = traceback.format_exc()[-2000:]
        fact("FATAL (a defect in THIS PYTHON SCRIPT or an unhandled read error, NOT a refusal by LabVIEW) "
             "%s: %s" % (type(e).__name__, str(e)[:200]))
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
