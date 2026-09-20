r"""probe_walk_stop_control.py - the NEGATIVE CONTROL the run-2 review called free, and it decides what M2 means.

M2's walk stopped with "owner uid N is NOT a node on any of the 170 CACHED diagrams". That sentence conflates
two different things (archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md section 4, "Free negative
control"): an object genuinely absent from `Diagram.Nodes[]`, and an object present in the VI but missing from
`tools/bench/main_vi_nodeterms.json`. The `EnumConstant` at uid 43955 is the oracle - a constant IS in the VI.

So: read diagram 10's Nodes[] LIVE (gscript.node_labels, not the cache) and ask, for each object the walk
stopped on, whether it is in that live list; and Traverse-count each object's class.

Read-only, nothing saved, no motor, no serial, no new op VI.

PREDICTION CONTRACT:
  N1 the live Nodes[] of diagram 10 has exactly the 2 uids the cache has (43997, 44036) - so the cache is not
     short for this diagram, and "not in the cache" == "not in Nodes[]" here.
  N2 uid 43605 (FlatSequenceOuterTunnel), 43955 (EnumConstant) and 43937 (VISAResourceNameConstant) are all
     ABSENT from that live Nodes[] list, while all three classes are Traverse-visible on the VI.
  N3 both originals' md5 unchanged.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

TRACKING = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ORIG = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
V6 = os.path.join(TRACKING, "Min_Track N beads V6_ParallelLoop.vi")
TARGETS = [(43605, "FlatSequenceOuterTunnel", "the T[8] Position source - the flat-sequence boundary"),
           (43955, "EnumConstant", "the T[9] Axis source - the ORACLE, a constant that is in the VI"),
           (43937, "VISAResourceNameConstant", "the T[10] VISA in source, 2 hops out"),
           (43997, "SubVI", "ASI Initialize.vi - a POSITIVE control, known to be in Nodes[]"),
           (44036, "SubVI", "the call site itself - positive control")]
OUT = os.path.join(HERE, "probe_walk_stop_control.json")
RES = {"gates": []}
_S = [0]


def must(l, ok, d=""):
    print(f"{'  PASS' if ok else '**FAIL'} {l}" + (f"  | {str(d)[:200]}" if d else ""), flush=True)
    RES["gates"].append({"label": l, "ok": bool(ok), "detail": str(d)[:300]})


def md5(p):
    try:
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    except Exception as e:
        _S[0] += 1
        return f"ERR#{_S[0]} {e}"


def main():
    before = {p: md5(p) for p in (ORIG, V6)}
    print(f"md5 before: { {os.path.basename(k): v for k, v in before.items()} }", flush=True)
    try:
        fresh()
        live = g.node_labels(V6, 10)
        live_uids = [r["uid"] for r in live]
        print(f"\nLIVE diagram 10 Nodes[]: {[(r['uid'], r['label']) for r in live]}", flush=True)
        with open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8") as f:
            cached = [n["uid"] for n in json.load(f)["diagrams"]["10"]["nodes"]]
        print(f"CACHED diagram 10 Nodes[]: {cached}", flush=True)
        RES["live_d10"] = [(r["uid"], r["label"]) for r in live]
        RES["cached_d10"] = cached
        must("N1 the cache is not short for diagram 10 (live == cached)", sorted(live_uids) == sorted(cached),
             f"live {sorted(live_uids)} vs cached {sorted(cached)}")
        rows = []
        for uid, cls, why in TARGETS:
            try:
                objs = g.report_all(V6, cls)
                n = len(objs)
                present = any(o["uid"] == uid for o in objs)
            except Exception as e:
                n, present = f"EXC {str(e)[:80]}", None
            r = {"uid": uid, "class": cls, "why": why, "in_live_d10_nodes": uid in live_uids,
                 "traverse_count_of_class": n, "found_by_traverse": present}
            print(f"   uid {uid:6d} {cls:26.26} in Nodes[d10]={r['in_live_d10_nodes']!s:5} "
                  f"Traverse({cls})={n} contains_it={present}   <- {why}", flush=True)
            rows.append(r)
        RES["targets"] = rows
        stops = [r for r in rows if r["uid"] in (43605, 43955, 43937)]
        must("N2 all three stop objects are ABSENT from Nodes[] yet Traverse-visible",
             all((not r["in_live_d10_nodes"]) and r["found_by_traverse"] for r in stops),
             str([(r["uid"], r["in_live_d10_nodes"], r["found_by_traverse"]) for r in stops]))
    finally:
        try:
            g.reset()
        except Exception:
            pass
        after = {p: md5(p) for p in (ORIG, V6)}
        must("N3 both originals' md5 unchanged",
             all(before[p] == after[p] and not str(before[p]).startswith("ERR#") for p in before),
             str({os.path.basename(k): v for k, v in after.items()}))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str)
        np_ = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {np_}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:44] for x in RES['gates'] if not x['ok']]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
