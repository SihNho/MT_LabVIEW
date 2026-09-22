r"""allterms_tmscclass - READ-ONLY: what Traverse class is a `To More Specific Class` node?

WHY (a measured ambiguity, not a hunch). `tools/bench/allterms_s2.log` run 2: Quick Drop opened, closed,
and the node IS ON THE DIAGRAM - the before/after crops of the SAME 130x90 region prove it
(`tools/bench/allterms_shots/z_before_crop.png` empty, `z_after_crop.png` the TMSC icon). Yet
`gscript.uids(work, "Function")` reported NO new uid. So either a TMSC is not traversed as `Function`,
or `report_all` cannot see a just-dropped node. This tells them apart WITHOUT another GUI act.

The control is a TMSC that has been on disk for days: `OpLoopCast_v0.vi` carries one, uid **683**
(`tools/bench/diag_allterms_retarget2.log:16` found it by its terminal names `target class` /
`specific class reference`, then took its index out of `g.report(p, "Function")`).

PREDICTION CONTRACT
  C1 `report(OpLoopCast_v0, "Function")` contains uid 683      (the retarget log's own route)
  C2 `report_all(OpLoopCast_v0, "Function")` contains uid 683  <- if this FAILS, `report_all`/`uids`
     is the defect and `report` is the reader S2 must use
  C3 `report_all(OpLoopCast_v0, "Node")` contains 683, and its reported `Class Name` NAMES the class

READ-ONLY: no copy, no edit, no save, no VI run, no GUI, no restart. The donor is opened through the
op VIs' own `Open VI Reference` only; its md5 is asserted before and after.
  py tools/bgrun.py --material --max-min 10 --log tools/bench/allterms_tmscclass.log -- py -u tools/bench/allterms_tmscclass.py
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gscript as g                                                                # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpLoopCast_v0.vi")
TMSC_UID = 683
FAILS = []


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(label, ok, detail=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)
    if not ok:
        FAILS.append(label)


def main():
    before = md5(DONOR)
    print("DONOR {0} md5 {1}".format(os.path.basename(DONOR), before), flush=True)

    rows = g.report(DONOR, "Function")
    uids = [o["uid"] for o in rows]
    gate("C1 report('Function') contains uid {0}".format(TMSC_UID), TMSC_UID in uids,
         "uids {0!r}".format(uids))
    for o in rows:
        print("   report  Function[{0}] uid {1} class {2!r} pos {3!r} owner {4!r}".format(
            o["i"], o["uid"], o["class"], o["pos"], o["owner"]), flush=True)

    rows2 = g.report_all(DONOR, "Function")
    uids2 = [o["uid"] for o in rows2]
    gate("C2 report_all('Function') contains uid {0}".format(TMSC_UID), TMSC_UID in uids2,
         "uids {0!r}".format(uids2))

    rows3 = g.report_all(DONOR, "Node")
    hit = [o for o in rows3 if o["uid"] == TMSC_UID]
    gate("C3 report_all('Node') contains uid {0}".format(TMSC_UID), bool(hit),
         "n_nodes {0} classes {1!r}".format(len(rows3), sorted({o["class"] for o in rows3})))
    if hit:
        print("   THE TMSC's OWN Traverse CLASS NAME: {0!r}  (pos {1!r} owner {2!r})".format(
            hit[0]["class"], hit[0]["pos"], hit[0]["owner"]), flush=True)

    after = md5(DONOR)
    gate("C4 the donor's md5 is unchanged", after == before, "{0} -> {1}".format(before, after))
    g.reset()
    print("ref_counts {0!r}".format(g.ref_counts()), flush=True)
    print("\n=== GATES: {0} pass / {1} fail{2}".format(
        4 - len(FAILS), len(FAILS), ("; failing: " + ", ".join(FAILS)) if FAILS else ""), flush=True)
    return 1 if FAILS else 0


sys.exit(main())
