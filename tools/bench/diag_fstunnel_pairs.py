r"""diag_fstunnel_pairs - connectivity-map STEP 4b, STEP A. READ-ONLY, on a dated scratch copy of S1.

QUESTION: can the machine give every flat-sequence tunnel's terminal set exactly, replacing vigraph's
equal-TOP + common-frame heuristic (23 of 58 outers paired, docs/toolkit-capabilities.md step-4 section)?

WHAT EXISTS AND IS REUSED (checked before writing): the uid-addressed readers `OpFsTunnelTerm_v0`
(FSOT OuterTerminal 3195B800 / InnerTerminal 3195B801) and `OpFsInnerTunnelTerm_v0` (FSIT LeftTerm 1C3A9000
/ RightTerm 1C3A9001), built 2026-09-18 by tools/recipes/build_opfstunnelterm_v2.py (38/38), called through
its poisoned `read_tunnel` via `wiki_build.read_fs_tunnels`. `OpTunnels_v0`/`gscript.tunnels` is NOT used:
it casts to `LoopTunnel` by Traverse index, and a flat-sequence tunnel is not a `Tunnel` (docs/NAMES.md:
1235-1236, `Tunnel` census has zero FlatSequence owners, NAMES.md:697). No new op VI.

PREDICTION CONTRACT
  P1 the scratch GObject census holds 58 FlatSequenceOuterTunnel and 518 FlatSequenceInnerTunnel (the wiki's)
  P2 every FSOT read returns OuterTerminal AND InnerTerminal uids with no face error (58/58)
  P3 each FSOT's two machine terminals == the two terminal rows the wiki attributes to that FSOT (58/58)
  P4 every FSIT read returns Left AND Right terminal uids; both are rows of the wiki terminal table
  P5 cross-class: OUT op on an FSIT uid, IN op on an FSOT uid -> refused (an error, no terminal)
  P6 S1 md5 unchanged, scratch deleted, refs opened == closed, no VI run but the op VIs
    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/diag_fstunnel_pairs.log -- py -u tools/bench/diag_fstunnel_pairs.py
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import wiki_build as W                                                             # noqa: E402

S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
WIKI_S1 = os.path.join(W.WIKI, "D1_s1_copy.json")


def body(s):
    s.start()
    s.discard_work()
    wiki = json.load(open(WIKI_S1, encoding="utf-8"))["terminals"]
    by_owner = collections.defaultdict(set)
    row_of = {}
    for r in wiki:
        by_owner[r["owner_uid"]].add(r["term_uid"])
        row_of[r["term_uid"]] = r
    s.head("[A1] GObject census of the scratch")
    objs, seen = [], set()
    for o in g.report_all(s.work, "GObject"):
        u = int(o["uid"])
        if u not in seen:
            seen.add(u)
            objs.append({"uid": u, "class": o["class"], "pos": tuple(o["pos"]), "owner": o["owner"]})
    n = collections.Counter(o["class"] for o in objs)
    s.gate("P1 58 FSOT / 518 FSIT", n["FlatSequenceOuterTunnel"] == 58 and n["FlatSequenceInnerTunnel"] == 518,
           "FSOT {0} FSIT {1}".format(n["FlatSequenceOuterTunnel"], n["FlatSequenceInnerTunnel"]))
    s.head("[A2] read every FS tunnel's two faces")
    rows = W.read_fs_tunnels(s.work, objs)
    s.R["fs_reads"] = rows
    out = [r for r in rows if r["class"] == "FlatSequenceOuterTunnel"]
    inn = [r for r in rows if r["class"] == "FlatSequenceInnerTunnel"]
    both = lambda r: bool(r["term_a"] and r["term_b"] and not r["err_a"] and not r["err_b"])
    s.gate("P2 FSOT both faces read", sum(map(both, out)) == 58, "{0}/58".format(sum(map(both, out))))
    exact = [r for r in out if {r["term_a"], r["term_b"]} == by_owner.get(r["uid"], set())]
    s.gate("P3 FSOT machine terminals == wiki rows of that FSOT", len(exact) == 58, "{0}/58".format(len(exact)))
    for r in [x for x in out if x not in exact][:8]:
        s.fact("P3 miss #{0}: machine {1} vs wiki {2}".format(r["uid"], (r["term_a"], r["term_b"]),
                                                              sorted(by_owner.get(r["uid"], ()))))
    ok_in = [r for r in inn if both(r)]
    in_wiki = [r for r in ok_in if r["term_a"] in row_of and r["term_b"] in row_of]
    s.gate("P4 FSIT both faces read AND both are wiki rows", len(in_wiki) == 518,
           "read {0}/518, in wiki {1}".format(len(ok_in), len(in_wiki)))
    own = collections.Counter((row_of[r["term_a"]]["owner_uid"] == r["uid"],
                               row_of[r["term_b"]]["owner_uid"] == r["uid"]) for r in in_wiki)
    s.fact("FSIT: wiki owner == the FSIT read (Left, Right): {0}".format(dict(own)))
    fr = collections.Counter((row_of[r["term_a"]].get("frame_diagram") != row_of[r["term_b"]].get("frame_diagram"))
                             for r in in_wiki)
    s.fact("FSIT: Left and Right on DIFFERENT frame_diagram: {0}".format(dict(fr)))
    errs = collections.Counter((r["class"], (r["err"] or "")[:40], (r["err_a"] or "")[:40], (r["err_b"] or "")[:40])
                               for r in rows if not both(r))
    s.fact("non-clean reads by (class, err, err_a, err_b): {0}".format(dict(errs)))
    s.head("[A3] cross-class refusal (class x property table)")
    T = K.mod("build_opfstunnelterm_v2")
    for kind, uid in (("IN", out[0]["uid"]), ("OUT", inn[0]["uid"])):
        lab = json.load(open(T.LABELS_IN if kind == "IN" else T.LABELS_OUT, encoding="utf-8"))
        r = T.read_tunnel(g.op(T.OP_IN if kind == "IN" else T.OP_OUT), lab, s.work, uid)
        s.R["cross_" + kind] = r
        s.gate("P5 {0} op on #{1} refused".format(kind, uid), not r["term_a_uid"] and bool(r["err_a"] or r["err"] or r["errs"]),
               "err {0!r} err_a {1!r} errs {2!r}".format(r["err"][:60], r["err_a"][:60], r["errs"][:60]))
    s.dump()


if __name__ == "__main__":
    st = K.Stage(S1, S1_MD5, "diag_fstunnel_pairs", preload=False, deadline_min=25,
                 task="connectivity-map step 4b step A: FS tunnel faces read from the machine")
    sys.exit(K.run(body, st))
