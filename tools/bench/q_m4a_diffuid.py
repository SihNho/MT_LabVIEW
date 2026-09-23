r"""q_m4a_diffuid - cycle 68 MATERIAL, READ-ONLY: M4a's P6b failed on diff(bed,new) rows whose endpoints are the SAME
uids with different terminal NAMES (stage_d1_m4a.log:293-295). This re-reads both files (dated scratch copies, deleted)
and diffs the edges keyed by TERMINAL UID instead of by name, and lists loop #23032's 'sr' pair edges in both.
Existing tools: stagekit.Stage.live_graph (wiki_build.read_live + jev_candidates.from_parts), vigraph.diff's edge set.
PREDICTION CONTRACT: U1 uid-keyed edges_removed == only #23499->#10429's edge; U2 uid-keyed edges_added all touch a new
node {23459, 9996, 23469, 23796}; U3 loop #23032 sr pair edges RECORDED for both (bed 2, new 3 expected).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import vigraph as V                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"
NEW = os.path.join(K.CLAUDEDEV, "D1_s3b_m4a_20260924_002708.vi")
NEW_MD5 = "bc519809937db449bc0c0ec2b6410c55"
NEWN = {23459, 9996, 23469, 23796}


def uedges(G):
    out, miss = set(), 0
    for k, a, b, _i in G["edges"]:
        ra, rb = G["rows"].get(a), G["rows"].get(b)
        if not ra or not rb:
            miss += 1
            continue
        out.add((k, V.key_parts(a)[0], int(ra.get("term_uid") or 0), V.key_parts(b)[0], int(rb.get("term_uid") or 0)))
    return out, miss


def main(s):
    s.start()
    s.discard_work()
    ret = K.json.load(open(os.path.join(K.BENCH, "decision_m3a4_v2.json"), encoding="utf-8"))["predict"][
        "diff_bed_new_nodes_removed"]
    new_sc = s.scratch("new", source=NEW)
    Gb = s.live_graph(s.work, ret)
    Gn = s.live_graph(new_sc, ret, {23032: [23469]})
    eb, mb = uedges(Gb)
    en, mn = uedges(Gn)
    s.fact("edges bed {0} (unkeyed {1}); new {2} (unkeyed {3})".format(len(eb), mb, len(en), mn))
    rem, add = sorted(eb - en), sorted(en - eb)
    s.fact("UID-KEYED edges_removed {0}".format(rem))
    s.fact("UID-KEYED edges_added {0}".format(add))
    wf = lambda E: [e for e in E if e[0] in ("wire", "fs")]           # review c68-m4a-p6b §4.2: sr reported, not gated
    s.gate("U1 uid-keyed wire/fs removed == only the #23499 -> #10429 edge",
           len(wf(rem)) == 1 and wf(rem)[0][1] == 23499 and wf(rem)[0][3] == 10429, wf(rem))
    s.gate("U2 every uid-keyed wire/fs added edge touches a new node", all({e[1], e[3]} & NEWN for e in wf(add)),
           wf(add))
    for tag, E, G in (("bed", eb, Gb), ("new", en, Gn)):
        s.fact("U3 {0} sr edges on #23032's registers: {1}".format(tag, sorted(
            e for e in E if e[0] == "sr" and {e[1], e[3]} & {23868, 23880, 23895, 23909, 23469, 23796})))
        s.fact("U3 {0} method['sr'] = {1}".format(tag, G.get("method", {}).get("sr")))
        pos = G.get("pos") or {}
        s.fact("U3 {0} pos: {1}".format(tag, dict((u, pos.get(u)) for u in (23868, 23880, 23895, 23909, 23469, 23796))))
        vk = [k for k in G["rows"] if V.key_parts(k)[0] == 48 and V.key_parts(k)[2] == "VISA resource name"]
        srcs = sorted(set(int(G["rows"][x].get("term_uid") or 0) for k in vk for x in V.sources_of(G, k)))
        eff = sorted(set(int(G["rows"][x].get("term_uid") or 0) for k in vk for x in V.effective_sources(G, k)))
        s.fact("U5 {0} #48 'VISA resource name': sources_of term uids {1}; effective_sources term uids {2}".format(
            tag, srcs, eff))
    li = s.uid_index("WhileLoop", 23032, target=new_sc)
    for k in range(3):
        r = K.g.shift_reg_left(new_sc, li, k)
        s.fact("U6 MACHINE: loop #23032 reg[{0}] right #{1} -> left #{2}".format(k, r.get("uid"), r["left"]["uid"]))
    s.gate("U4 the M4a artefact md5 unchanged", K.md5(NEW) == NEW_MD5, K.md5(NEW))
    s.drop_scratch(new_sc)


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "q_m4a_diffuid", preload=False, deadline_min=15, reserve_s=200,
                 pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5), ("M4a", NEW, NEW_MD5)),
                 task="cycle 68: M4a P6b - uid-keyed diff(bed, M4a)")
    sys.exit(K.run(main, st))
