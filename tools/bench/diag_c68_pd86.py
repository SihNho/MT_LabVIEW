"""diag_c68_pd86 - THE FIRST ACT OF THE CYCLE (Pre-decided 86, docs/cycle27-plan.md:3040-3052).

ONE QUESTION, NO MUTATION: is `OpWireSource_v5` (wire_source_owner) a sound reader?
Three named outcomes, decided by the machine, never by inference:
  A  an UNRESOLVABLE uid returns rows with 0 REAL owners  -> the reader NULLS on an unresolvable uid
     (the signature already seen for 9649 at build_d1_m3a1.log:1071 and 23955 at :1150).
  B  an unresolvable query returns the PREVIOUS call's answer -> a STALE ECHO; every identity conclusion
     of cycles 55/56 is VOID, including the ones that passed.
  C  an unresolvable uid returns a CLEAN ERROR -> the reader is sound; the cycle-56 anomaly was a
     deferred edit (separated below by reading the same live uid twice, 1 s apart, with no edit between).

QUERIES, in this exact order (order matters for the echo test):
  Q1 WIRE_TERMS(24009)      - a uid minted only in cycle 56's dead in-memory session; absent from the bed
  Q2 WIRE_TERMS(2147483647) - unresolvable by construction
  Q3 WIRE_TERMS(9649)       - LIVE (T1_OUTER_WIRE on the bed; pre-write walk read recip=9649, log:1061-1063)
  Q4 WIRE_TERMS(9649) again after 1.0 s, NO edit between - the deferred-edit separator
  Q5 WIRE_TERMS(9113)       - LIVE (t6's original net) - the Pre-decided 85 precondition sample

Pre-decided 85 precondition, measured here retroactively: every row of a LIVE walk must satisfy
`recip == queried_uid`. Reported as FACT lines; per Pre-decided 63 THIS RUN GATES ON HYGIENE ONLY
(md5 pins, scratch removed, refs balanced, handles read) and exits 0 when hygiene passes.
NO MUTATOR IS IMPORTED OR CALLED. The bed is only ever COPIED; the copy is deleted at exit.
No motor / ASI / camera (rig ASSEMBLED). No new op, verb or device. No GUI action.
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("S1 D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))

UID_GHOST = 24009          # minted in cycle 56's in-memory session only (build_d1_m3a1.log:473); not on disk
UID_MAX = 2147483647
UID_LIVE_1 = 9649          # T1_OUTER_WIRE - live on the bed
UID_LIVE_2 = 9113          # t6's original net - live on the bed

STAMP = time.strftime("%Y%m%d_%H%M%S")
WORK = os.path.join(g.CLAUDEDEV, "PD86_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "diag_c68_pd86.json")

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "Pre-decided 86 - reader-identity discriminating test, NO MUTATION",
     "gating_policy": "Pre-decided 63: HYGIENE ONLY - measurements are FACT lines",
     "no_mutator_called": True, "no_gui_action": True, "no_new_device": True,
     "rig_state": "assembled - no motor, no ASI, no camera",
     "handles": {}, "walks": {}, "verdict": {}}


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  %r" % detail) if detail else ""), flush=True)


def fact(line):
    facts.append(line)
    print("  FACT  %s" % line, flush=True)


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=repr)


def walk(tag, uid):
    """One query; every row a FACT line; the raw result + verbatim error recorded."""
    rows, err = [], ""
    try:
        rows = WIRE_TERMS(WORK, int(uid)) or []
    except Exception as e:                                                         # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
    real = [t for t in rows if t.get("owner_uid")]
    fact("%s OpWireSource_v5(UID 2 = %r): %d row(s), %d with a REAL owner%s"
         % (tag, uid, len(rows), len(real), (" ; ERROR " + err) if err else ""))
    for t in rows:
        fact("    %s t%-2r is_source=%-5r owner_class=%-26r owner_uid=%-7r recip=%r%s"
             % (tag, t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"),
                t.get("recip"), ("  READ ERROR " + str(t["err"])) if t.get("err") else ""))
    R["walks"][tag] = {"uid": uid, "rows": rows, "n_real_owner": len(real), "error_verbatim": err}
    dump()
    return rows, real, err


def rows_equal(a, b):
    key = lambda t: (t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"), t.get("recip"))  # noqa: E731
    return [key(t) for t in (a or [])] == [key(t) for t in (b or [])]


def main():
    print("=== diag_c68_pd86  %s  (Pre-decided 86 - one op call, no mutation)" % STAMP, flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    for tag, path, pin in PINS:
        ff = D.file_facts("H %s BEFORE" % tag, path)
        gate("H %s md5 == its pin %s" % (tag, pin[:8]), ff.get("md5") == pin, ff.get("md5"))
    fact("pre-batch LabVIEW restart (STATUS NEXT: 38,316 handles left running after cycle 56)")
    D.fresh("[0] pre-batch LabVIEW restart")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    shutil.copy2(BED, WORK)
    ff = D.file_facts("[1] the scratch copy", WORK)
    gate("H the scratch starts byte-identical to the bed", ff.get("md5") == BED_MD5, ff.get("md5"))

    try:
        # ---- THE FOUR QUERIES, in the order Pre-decided 86 names
        q1_rows, q1_real, q1_err = walk("[Q1 GHOST 24009]", UID_GHOST)
        q2_rows, q2_real, q2_err = walk("[Q2 MAX 2147483647]", UID_MAX)
        q3_rows, q3_real, q3_err = walk("[Q3 LIVE 9649 read A]", UID_LIVE_1)
        fact("sleeping 1.0 s - NO edit of any kind between read A and read B")
        time.sleep(1.0)
        q4_rows, q4_real, q4_err = walk("[Q4 LIVE 9649 read B]", UID_LIVE_1)
        q5_rows, q5_real, q5_err = walk("[Q5 LIVE 9113]", UID_LIVE_2)

        # ---- CLASSIFICATION - FACT LINES, NEVER GATES (Pre-decided 63)
        echo_q2_of_q1 = bool(q1_rows) and rows_equal(q2_rows, q1_rows)
        clean_error = bool(q1_err) and bool(q2_err)
        if echo_q2_of_q1:
            verdict = ("B-STALE-ECHO", "Q2 (2147483647) returned Q1's rows field-for-field - the reader "
                       "echoes the previous call; EVERY identity conclusion of cycles 55/56 is VOID "
                       "(Pre-decided 86 outcome B)")
        elif clean_error:
            verdict = ("C-CLEAN-ERROR", "both unresolvable uids raised a clean error - the reader is sound; "
                       "the cycle-56 anomaly points at a deferred edit (outcome C)")
        elif all(not re_ for re_ in (q1_real, q2_real)):
            verdict = ("A-READER-NULLS", "both unresolvable uids returned rows with 0 REAL owners - the "
                       "reader nulls on an unresolvable uid (outcome A); the disappearing sink and the uid "
                       "alarm collapse into one reader behaviour")
        else:
            verdict = ("MIXED", "the three named signatures did not fire cleanly - the raw walks above are "
                       "the record; judgement decides (Q1 real=%d err=%r ; Q2 real=%d err=%r)"
                       % (len(q1_real), q1_err, len(q2_real), q2_err))
        R["verdict"]["outcome"] = verdict[0]
        fact("*** PRE-DECIDED 86 OUTCOME: %s - %s ***" % verdict)

        stable = rows_equal(q3_rows, q4_rows)
        R["verdict"]["live_read_stable"] = stable
        fact("*** LIVE READ STABILITY (deferred-edit separator): 9649 read A == read B field-for-field: %r ***"
             % stable)
        for tag, uid, rows in (("Q3", UID_LIVE_1, q3_rows), ("Q4", UID_LIVE_1, q4_rows),
                               ("Q5", UID_LIVE_2, q5_rows)):
            bad = [t for t in rows if t.get("recip") != uid]
            fact("*** PRE-DECIDED 85 PRECONDITION on %s (uid %d): %d row(s), %d violate recip==queried_uid%s"
                 % (tag, uid, len(rows), len(bad),
                    (" -> " + repr([(t.get("i"), t.get("recip")) for t in bad])) if bad else " ***"))
            R["verdict"]["pd85_%s" % tag] = {"rows": len(rows), "recip_violations": len(bad)}
    finally:
        try:
            g.close_panel(WORK)
        except Exception:                                                          # noqa: BLE001
            pass
        if os.path.exists(WORK):
            try:
                os.remove(WORK)
            except Exception as e:                                                 # noqa: BLE001
                fact("scratch remove failed: %r" % e)
        gate("H scratch %s is gone" % os.path.basename(WORK), not os.path.exists(WORK))
        for tag, path, pin in PINS:
            ff = D.file_facts("H %s AFTER" % tag, path)
            gate("H %s md5 STILL its pin %s" % (tag, pin[:8]), ff.get("md5") == pin, ff.get("md5"))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        gate("H refs opened == closed and 0 live", rc.get("live") == 0, rc)
        R["handles"]["after"] = labview_handles()
        gate("H handle count read at entry and exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
