r"""probe_flatseq_outer.py - cycle 19 follow-up. TWO measurements the run-2 reviews said were missing.
Read-only, nothing saved, no motor, no serial. One runner, one bgrun.

T1 (both review arms, archive/peer/2026-09-18-walk-run2-flatseq-crossing-{codex,opus}.md): the walk from the
   ASI startup site stopped on **FlatSequenceOuterTunnel**, a DIFFERENT class from the FlatSequenceInnerTunnel
   that probe_flatseq_walk measured. Its documented ids are 3195B800 Outer Terminal / 3195B801 Inner Terminal /
   3195B802 Frame - and 3195B801 has been in this project's own files since 2026-09-14
   (archive/peer/2026-09-14-optunnels-v0-plan.md:45). So: run the SAME property-attachment census against
   `VI Server:FlatSequenceOuterTunnel` and report which ids attach and under which short names.

T2 (M3 sensitivity): probe_flatseq_walk_run2 reported "0 limiting-construct matches" for every motion subVI.
   That is only meaningful if gscript.node_labels can SEE an unlabelled primitive. Dump every label verbatim
   and count how many node rows carry a non-empty one, so "0 matches" is reported with its real sensitivity.

REUSE: gscript.build_property / node_labels / node_terms / count / uids, the scratch-VI pattern from
tools/bench/census_dnc_property_ids.py. NO new op VI. One scratch VI, created and deleted in the same run.

PREDICTION CONTRACT:
  T1a the class string 'VI Server:FlatSequenceOuterTunnel' resolves (632A813 control ATTACHES).
  T1b 3195B800 / 3195B801 / 3195B802 all ATTACH and report short names.
  T1c 1C3A9000 ('LeftTerm', an INNER-tunnel id) is REFUSED with 1077 on the OUTER class - i.e. the two classes
      are genuinely distinct and the run-2 census does not transfer.
  T2a node_labels returns one row per node and >= 1 non-empty label somewhere.
  T2b the originals' md5 and every motion subVI's md5 are unchanged before and after.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

TRACKING = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ORIG_3STATE = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
V6 = os.path.join(TRACKING, "Min_Track N beads V6_ParallelLoop.vi")
SCR = os.path.join(g.CLAUDEDEV, "OpFsotProbe_scratch_c19.vi")
SRC_FOR_SCRATCH = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")

LV = r"C:\Program Files\National Instruments\LabVIEW 2026"
MERC = os.path.join(LV, r"instr.lib\Mercury\GCS_LabVIEW\Low Level")
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
VIS = [
    ("MOV.vi", os.path.join(MERC, r"General command.llb\MOV.vi"), os.path.join(MERC, "General command.llb")),
    ("VEL.vi", os.path.join(MERC, r"General command.llb\VEL.vi"), os.path.join(MERC, "General command.llb")),
    ("GOH.vi", os.path.join(MERC, r"Limits.llb\GOH.vi"), os.path.join(MERC, "Limits.llb")),
    ("TMX?.vi", os.path.join(MERC, r"Limits.llb\TMX?.vi"), os.path.join(MERC, "Limits.llb")),
    ("ASI Move Axis to Position.vi", os.path.join(LV, r"instr.lib\ASI TG-1000\Public\Action\Move Axis to Position.vi"), None),
    ("Autonics SetCommand.vi", os.path.join(LV, r"instr.lib\Autonics Motor\SetCommand.vi"), None),
    ("Max Trans Pos.vi", os.path.join(LAB, r"DY\Background VIs\Max Trans Pos.vi"), None),
]
VIS = [(n, p, c or p) for n, p, c in VIS]
FILES = [ORIG_3STATE, V6] + sorted({c for _n, _p, c in VIS})
OUT = os.path.join(HERE, "probe_flatseq_outer.json")
RES = {"gates": [], "t1": [], "t2": {}, "md5": {}}
_SEQ = [0]

OUTER_CLASS = "VI Server:FlatSequenceOuterTunnel"
T1_IDS = [("632A813", "CONTROL GObject.UID"), ("6327803", "CONTROL Generic.Class Name"),
          ("3195B800", "Outer Terminal (peer)"), ("3195B801", "Inner Terminal (peer; in our files since 09-14)"),
          ("3195B802", "Frame (peer)"), ("3195B803", "block census, undocumented"),
          ("1C3A9000", "INNER-tunnel LeftTerm - must NOT attach here"),
          ("634A002", "Terminal.Diagram - inheritance probe")]
SKIP = ("reference", "reference out", "error in (no error)", "error out")
LIMIT_PAT = ["in range and coerce", "coerce", "max & min", "max&min", "min & max", "clip",
             "greater", "less", "select", "maximum", "minimum", "limit"]


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:200]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return ok


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        _SEQ[0] += 1
        return f"ERR#{_SEQ[0]} {e}"


def snapshot(tag):
    d = {p: md5(p) for p in FILES}
    RES["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for p, h in d.items():
        print(f"   {h}  {os.path.basename(p)}", flush=True)
    return d


def t1():
    print("\n================ T1: FlatSequenceOuterTunnel property census ================", flush=True)
    if os.path.exists(SCR):
        os.remove(SCR)
    shutil.copyfile(SRC_FOR_SCRATCH, SCR)
    time.sleep(0.4)
    rows = []
    try:
        g.open_panel(SCR)
        time.sleep(0.8)
        y = 260
        for pid, why in T1_IDS:
            before = g.uids(SCR, "Property")
            rec = {"id": pid, "why": why}
            try:
                g.build_property(SCR, OUTER_CLASS, [(pid, False)], (1500, y))
                y += 110
                new = [u for u in g.uids(SCR, "Property") if u not in before]
                if len(new) != 1:
                    rec["outcome"] = f"{len(new)} new property nodes (expected 1)"
                else:
                    labs = g.node_labels(SCR, 0)
                    i = [k for k, r in enumerate(labs) if r["uid"] == new[0]]
                    names = []
                    if i:
                        names = [r["name"] for r in g.node_terms(SCR, 0, i[0]) if r["name"] not in SKIP]
                    rec["outcome"] = "ATTACHED"
                    rec["short_names"] = names
            except Exception as e:
                rec["outcome"] = f"REFUSED {str(e)[:180]}"
            print(f"   {pid} [{why}] -> {rec['outcome']}"
                  + (f"  short names {rec.get('short_names')}" if "short_names" in rec else ""), flush=True)
            rows.append(rec)
    finally:
        try:
            g.close_panel(SCR)
        except Exception:
            pass
        time.sleep(0.5)
        if os.path.exists(SCR):
            os.remove(SCR)
            print("   scratch VI deleted", flush=True)
    RES["t1"] = rows
    by = {r["id"]: r.get("outcome") for r in rows}
    must("T1a the class string 'VI Server:FlatSequenceOuterTunnel' resolves", by.get("632A813") == "ATTACHED",
         by.get("632A813"))
    must("T1b 3195B800 / 3195B801 / 3195B802 all ATTACH",
         all(by.get(i) == "ATTACHED" for i in ("3195B800", "3195B801", "3195B802")),
         {i: by.get(i) for i in ("3195B800", "3195B801", "3195B802")})
    must("T1c the INNER-tunnel id 1C3A9000 does NOT attach to the OUTER class (the classes are distinct)",
         by.get("1C3A9000") != "ATTACHED", by.get("1C3A9000"))
    # how many of each boundary class does the working copy hold?
    for cls in ("FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel", "FlatSequence", "FlatSequenceFrame"):
        try:
            n = g.count(V6, cls)
        except Exception as e:
            n = f"EXC {str(e)[:90]}"
        print(f"   count(V6, {cls!r}) = {n}", flush=True)
        RES["t2"].setdefault("class_counts", {})[cls] = n


def t2():
    print("\n================ T2: M3 label-scan sensitivity ================", flush=True)
    out = {}
    for name, path, _c in VIS:
        print(f"\n   === {name}", flush=True)
        rec = {"path": path, "diagrams": {}}
        try:
            nd = int(g.count(path, "Diagram"))
        except Exception as e:
            print(f"       count(Diagram) RAISED {str(e)[:150]}", flush=True)
            out[name] = {"err": str(e)[:200]}
            continue
        tot = named = 0
        hits = []
        for di in range(nd):
            try:
                rows = g.node_labels(path, di)
            except Exception as e:
                print(f"       d{di}: node_labels RAISED {str(e)[:110]}", flush=True)
                continue
            labs = [r["label"] for r in rows]
            tot += len(rows)
            named += sum(1 for x in labs if x.strip())
            rec["diagrams"][di] = [{"uid": r["uid"], "label": r["label"]} for r in rows]
            if rows:
                print(f"       d{di}: {[x if x else '<EMPTY>' for x in labs]}", flush=True)
            for r in rows:
                lo = (r["label"] or "").lower()
                if any(p in lo for p in LIMIT_PAT):
                    hits.append({"d": di, "uid": r["uid"], "label": r["label"]})
        rec["nodes_total"] = tot
        rec["labels_nonempty"] = named
        rec["limit_hits"] = hits
        print(f"       TOTAL {tot} node rows, {named} non-empty labels "
              f"({(named / tot * 100) if tot else 0:.0f} %), limit matches {len(hits)}", flush=True)
        out[name] = rec
    RES["t2"]["vis"] = out
    tots = [v for v in out.values() if "nodes_total" in v]
    must("T2a node_labels returned rows and at least one non-empty label overall",
         bool(tots) and sum(v["labels_nonempty"] for v in tots) >= 1,
         str({k: (v.get("nodes_total"), v.get("labels_nonempty")) for k, v in out.items()}))


def main():
    print("PREDICTION CONTRACT T1a..T2b - see this file's docstring.", flush=True)
    before = snapshot("before")
    try:
        fresh()
        t1()
        t2()
    finally:
        try:
            g.reset()
        except Exception:
            pass
        after = snapshot("after")
        must("T2b every pre-existing .vi md5 unchanged",
             all(before[p] == after[p] and not str(before[p]).startswith("ERR#") for p in FILES),
             str([os.path.basename(p) for p in FILES if before[p] != after[p]]))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, ensure_ascii=False, default=str)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:44] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
