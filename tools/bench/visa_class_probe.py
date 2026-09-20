"""visa_class_probe.py - which VI Scripting CLASS is a VISA Write node, and does VI.Callees exist?

WHY (prior art checked before writing a line, CLAUDE.md "before creating any new op/tool/recipe"):
  * docs/main-vi-subvi-identity.md - 98 call sites x 56 callees of the WORKING COPY
    `Min_Track N beads V6_ParallelLoop.vi`, measured 2026-09-14 by tools/bench/sweep_subvis_main.py
    (OpSubVIs_v1).  It is a per-diagram subVI IDENTITY listing; it classifies nothing.
  * docs/instrument-libraries.md:167-169 - the library-level counts the plan quotes.
  * docs/motion-path-audit.md - PI MOV/VEL send + error-query; ASI's writes funnel through
    `Send Serial Command.vi` (VISA Write/Read inside a semaphore).
  * tools/callgraph.py - OFFLINE byte-scan of subVI name references; cannot see call sites or VISA.
  NONE of them decides a call site by REACHABILITY TO A SERIAL WRITE, which is the census's
  PRIMARY rule.  So a new reader is needed; this probe measures the one fact it depends on.

OFFLINE ROUTE ALREADY REFUTED (2 scratchpad probes, no LabVIEW): a .vi's raw bytes and every zlib
blob in it do NOT contain "VISA Write" even for SetCommand.vi, which is MEASURED to contain one
(tools/recipes/build_setcommand_signed.py:5 "VISA Write 795 -> VISA Read 926").  Only the VISA
*terminal* names ("VISA resource name", "write buffer") survive.  Hence a COM class read.

READ-ONLY.  Nothing is run, edited or saved.  No motor port is opened.

PREDICTION CONTRACT (printed before the run, machine-checked after)
 P1  report_all(SetCommand.vi,"Node") returns >= 1 row, and a row with uid 795 exists.
 P2  that row's class is a non-empty string -> SERIAL_WRITE_CLASS for the census.
 P3  that class occurs >= 1x in ASI `Send Serial Command.vi` and 0x in `Max Trans Pos.vi`
     (docs/motion-path-audit.md:80 calls the latter effectively empty).
 P4  md5 of the two originals unchanged across the whole run.
 P5  lv().GetVIReference(...).Callees either returns a sequence (cheap call-graph route) or the
     exception text is recorded verbatim.

    MATERIAL=1 py tools/bgrun.py --max-min 8 --log tools/bench/visa_class_probe.log \
        -- py -u tools/bench/visa_class_probe.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "tools"))
import gscript as g                                                            # noqa: E402

LV = r"C:\Program Files\National Instruments\LabVIEW 2026"
TRACK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
ORIG_3STATE = os.path.join(TRACK, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
ORIG_V6 = os.path.join(TRACK, "Min_Track N beads V6_ParallelLoop.vi")
SETCMD = os.path.join(LV, r"instr.lib\Autonics Motor\SetCommand.vi")
ASISER = os.path.join(LV, r"instr.lib\ASI TG-1000\Public\Utility\Send Serial Command.vi")
MAXTRANS = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\DY\Background VIs\Max Trans Pos.vi"
OUT = os.path.join(HERE, "visa_class_probe.json")


def md5(p):
    if not os.path.exists(p):
        return "MISSING"
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    res = {"md5_before": {}, "md5_after": {}, "gates": {}}
    for tag, p in (("3state", ORIG_3STATE), ("v6", ORIG_V6)):
        res["md5_before"][tag] = md5(p)
        print("MD5 BEFORE %-8s %s  %s" % (tag, res["md5_before"][tag], p), flush=True)
    print("PREDICTION P1 uid 795 present in report_all(SetCommand.vi,'Node')", flush=True)
    print("PREDICTION P2 its class is non-empty", flush=True)
    print("PREDICTION P3 that class >=1 in ASI Send Serial Command.vi, 0 in Max Trans Pos.vi", flush=True)
    print("PREDICTION P4 both originals' md5 unchanged", flush=True)
    print("PREDICTION P5 VI.Callees returns a sequence, or the error is recorded", flush=True)

    g._lv = None
    try:
        rows = g.report_all(SETCMD, "Node")
        res["setcmd_nodes"] = rows
        print("SETCMD nodes=%d" % len(rows), flush=True)
        by_class = {}
        for r in rows:
            by_class.setdefault(r["class"], []).append(r["uid"])
        for c in sorted(by_class):
            print("   class %-28s n=%-3d uids=%s" % (c, len(by_class[c]), by_class[c][:12]), flush=True)
        hit = [r for r in rows if r["uid"] == 795]
        res["gates"]["P1"] = bool(hit)
        cls = hit[0]["class"] if hit else ""
        res["serial_write_class"] = cls
        res["gates"]["P2"] = bool(cls)
        print("P1 uid795 %s  -> class %r" % ("PASS" if hit else "FAIL", cls), flush=True)

        # label every node of SetCommand.vi so the class can be named in prose, not guessed
        nd = int(g.count(SETCMD, "Diagram"))
        labels = {}
        for d in range(nd):
            try:
                for r in g.node_labels(SETCMD, d, strict=False)[0]:
                    labels[r["uid"]] = r["label"]
            except Exception as e:
                print("   node_labels(%d) EXC %s" % (d, str(e)[:100]), flush=True)
        res["setcmd_labels"] = {str(k): v for k, v in labels.items()}
        for r in rows:
            if labels.get(r["uid"]):
                print("   uid %-7d %-28s |%s|" % (r["uid"], r["class"], labels[r["uid"]][:50]), flush=True)

        if cls:
            n_asi = len(g.report_all(ASISER, cls))
            n_neg = len(g.report_all(MAXTRANS, cls))
            res["asi_count"], res["neg_count"] = n_asi, n_neg
            res["gates"]["P3"] = (n_asi >= 1 and n_neg == 0)
            print("P3 %s  ASI Send Serial Command=%d  Max Trans Pos=%d"
                  % ("PASS" if res["gates"]["P3"] else "FAIL", n_asi, n_neg), flush=True)
        else:
            res["gates"]["P3"] = False

        try:
            vref = g.lv().GetVIReference(SETCMD, "", False, 0)
            cal = list(vref.Callees)
            res["callees_setcmd"] = [str(x) for x in cal]
            res["gates"]["P5"] = True
            print("P5 PASS VI.Callees -> %r" % (res["callees_setcmd"][:20],), flush=True)
            vref = None
        except Exception as e:
            res["callees_error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            res["gates"]["P5"] = False
            print("P5 FAIL VI.Callees -> %s" % res["callees_error"], flush=True)
    finally:
        try:
            g.reset()
        except Exception:
            pass

    ok = True
    for tag, p in (("3state", ORIG_3STATE), ("v6", ORIG_V6)):
        res["md5_after"][tag] = md5(p)
        same = res["md5_after"][tag] == res["md5_before"][tag]
        ok = ok and same
        print("MD5 AFTER  %-8s %s  %s" % (tag, res["md5_after"][tag], "SAME" if same else "*** CHANGED ***"),
              flush=True)
    res["gates"]["P4"] = ok
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    npass = sum(1 for v in res["gates"].values() if v)
    print("GATES %d/%d pass: %s" % (npass, len(res["gates"]), res["gates"]), flush=True)
    print("PROBE DONE -> %s" % OUT, flush=True)
    return 0 if res["gates"].get("P4") else 2


if __name__ == "__main__":
    sys.exit(main())
