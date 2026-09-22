r"""STEP 4a of docs/connectivity-map-plan.md - the ONE LabVIEW phase of step 4. READ-ONLY.

PREDICTION CONTRACT (machine-checkable, written before the run):
  A1  wiki_build --op v1 --force returns rc 0; docs/wiki/index.json holds 96 entries, 96 JSON files
      exist, every index md5 == the file's md5 on disk, 0 unread.
  A2  every re-read JSON's terminal rows carry the 7th column `frame_diagram` (checked on the bed, the
      S1 copy and 3 subVIs); on the bed `frame_diagram` is non-zero on every Inner/Frame-owner row.
  B1  a GObject census (uid, class, pos, owner-class) is dumped for the S1 copy and the bed - step 4b
      needs POSITIONS, which the wiki JSON does not keep.
  C1  loop_cast() over every ForLoop and WhileLoop of both VIs yields `Shift Registers[]` per loop; the
      union of right-register uids EQUALS the VI's RightShiftRegister count (36 on S1, 38 on the bed).
  H   pins hold at both ends (ORIGINAL + 4 claudeDev files + both op VIs), no VI is run, nothing is
      saved outside what wiki_build already does (its own scratch EMPTY copies, which it deletes),
      no motor / ASI / camera.

WHAT ALREADY EXISTS (checked before writing, CLAUDE.md "check what exists first"):
  tools/wiki_build.py (--op v1 is already a flag), tools/allterms.py, tools/vigraph.py, gscript.report_all,
  gscript.loop_cast (ForLoop + WhileLoop), gscript.count. NOTHING NEW IS BUILT HERE - this file only
  sequences readers that exist and writes their output to disk.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import stagekit as K                                                               # noqa: E402
import wiki_build as W                                                             # noqa: E402

DATE = time.strftime("%Y%m%d")
S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
PINS = [("ORIGINAL", g.ORIGINAL, g.ORIG_MD5),
        ("S1", S1, "3e3d23cefd3a334001aa9d6156bf1aee"),
        ("bed", BED, "0b84595245dd650c0e8fd3f57104782c"),
        ("OpAllTerms_v0", os.path.join(g.CLAUDEDEV, "OpAllTerms_v0.vi"),
         "484853aad3a9c2819d7fd36028491a81"),
        ("OpAllTerms_v1", os.path.join(g.CLAUDEDEV, "OpAllTerms_v1.vi"),
         "457a8d732a0e219e9aeddbeafbb38c1d")]
N = {"pass": 0, "fail": 0}


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label,
                                 (" | " + str(detail)[:300]) if detail else ""), flush=True)


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def pins(when):
    bad = [n for n, p, m in PINS if not os.path.exists(p) or K.md5(p) != m]
    gate("pins hold {0}".format(when), not bad, "broken: {0}".format(bad) if bad else "5/5")
    return not bad


def dump(name, payload):
    p = os.path.join(HERE, "{0}_{1}.json".format(name, DATE))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    fact("wrote {0} ({1:.1f} KB)".format(os.path.basename(p), os.path.getsize(p) / 1024.0))
    return p


def main():
    t0 = time.time()
    print("=== STEP 4a  v1 wiki + positions + Shift Registers[]  {0}".format(
        time.strftime("%Y-%m-%d %H:%M:%S")), flush=True)
    if not pins("before"):
        return 2
    bp = K.mod("bench_prep")
    fact("handles before: {0!r}".format(bp.labview_handles()))

    # ---- A: the wiki on the 7-column reader --------------------------------------------------
    ta = time.time()
    rc = W.main(["--op", "v1", "--force"])
    fact("wiki_build --op v1 --force rc={0} in {1:.0f}s".format(rc, time.time() - ta))
    idx = json.load(open(W.INDEX, encoding="utf-8"))["vis"]
    stale = [k for k, v in idx.items() if not os.path.exists(v["file"]) or K.md5(v["file"]) != v["md5"]]
    missing = [k for k in idx if not os.path.exists(os.path.join(W.WIKI, k + ".json"))]
    gate("A1 96 entries, md5s match, none missing, rc 0",
         len(idx) == 96 and not stale and not missing and rc == 0,
         "n={0} stale={1} missing={2} rc={3}".format(len(idx), stale[:4], missing[:4], rc))

    probe = ["D1_s1_copy", "D1_s3b_m3a3b_rowD_20260922_161040"] + \
            sorted(k for k in idx if k not in ("D1_s1_copy",))[:3]
    no7 = []
    for k in probe:
        rec = json.load(open(os.path.join(W.WIKI, k + ".json"), encoding="utf-8"))
        if not rec["terminals"] or "frame_diagram" not in rec["terminals"][0]:
            no7.append(k)
    gate("A2a frame_diagram present on 5 probed wikis", not no7, "missing on {0}".format(no7))
    bedrec = json.load(open(os.path.join(W.WIKI, os.path.basename(BED)[:-3] + ".json"), encoding="utf-8"))
    inner = [r for r in bedrec["terminals"] if "Inner" in r.get("term_class", "") or
             "Frame" in r.get("owner_class", "")]
    zero = [r for r in inner if not r.get("frame_diagram")]
    gate("A2b bed inner/frame rows all carry a frame", inner and not zero,
         "{0} inner rows, {1} with frame 0".format(len(inner), len(zero)))

    # ---- B: positions (the wiki keeps no GObject census) --------------------------------------
    for tag, path in (("s1", S1), ("bed", BED)):
        t = time.time()
        objs, seen = [], set()
        for o in g.report_all(path, "GObject"):
            u = int(o["uid"])
            if u in seen:
                continue
            seen.add(u)
            objs.append({"uid": u, "class": o["class"], "pos": list(o["pos"]), "owner": o["owner"]})
        fact("B {0}: {1} objects in {2:.1f}s".format(tag, len(objs), time.time() - t))
        dump("graph_objs_" + tag, {"vi": path, "md5": K.md5(path), "n": len(objs), "objects": objs})

    # ---- C: Shift Registers[] per loop, the exact route ---------------------------------------
    for tag, path in (("s1", S1), ("bed", BED)):
        t, loops, errs = time.time(), [], []
        for cls in ("ForLoop", "WhileLoop"):
            n = g.count(path, cls)
            for i in range(n):
                try:
                    r = g.loop_cast(path, i, cls)
                except Exception as e:                                             # noqa: BLE001
                    errs.append("{0}[{1}]: {2}".format(cls, i, str(e)[:120]))
                    continue
                loops.append({"class": cls, "index": i, "loop_uid": int(r["loop_uid"]),
                              "right_uids": [int(u) for u in r["shift_reg_uids"]],
                              "errors": {k: v for k, v in (r.get("errors") or {}).items() if v}})
        rights = sorted({u for L in loops for u in L["right_uids"]})
        want = g.count(path, "RightShiftRegister")
        fact("C {0}: {1} loops, {2} right registers in {3:.0f}s; op errors {4}".format(
            tag, len(loops), len(rights), time.time() - t, errs[:2] or "none"))
        gate("C1 {0}: Shift Registers[] union == RightShiftRegister count".format(tag),
             len(rights) == want and not errs, "{0} vs {1}".format(len(rights), want))
        dump("graph_loops_" + tag, {"vi": path, "md5": K.md5(path), "loops": loops,
                                    "right_uids": rights, "errors": errs})

    pins("after")
    fact("handles after: {0!r}".format(bp.labview_handles()))
    left = sorted(f for f in os.listdir(g.CLAUDEDEV) if f.lower().startswith("wikipane_"))
    gate("H scratch EMPTY copies all removed", not left, "left: {0}".format(left[:5]))
    fact("total {0:.0f}s".format(time.time() - t0))
    print("=== STEP 4a: {0} pass / {1} fail".format(N["pass"], N["fail"]), flush=True)
    return 1 if N["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
