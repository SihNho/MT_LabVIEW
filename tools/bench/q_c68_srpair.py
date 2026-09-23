r"""q_c68_srpair - cycle 68 MATERIAL, READ-ONLY on dated scratches (deleted). NO VI run, no motor/ASI/camera.
EXISTING TOOLS (checked first): stagekit.Stage (restart, scratch, pins, hygiene), wiki_build.read_live + jev_candidates
.from_parts (= Stage.live_graph's recipe, stagekit.py:802), gscript.loop_cast / shift_reg_left (OpShiftRegs_v1 =
RightShiftRegister.Left Registers[]), build_opcreateconstonterm_v0.read_const (OpConstValueN_v1), vigraph.diff /
computation_diff. vigraph.build4 now takes loops[].left_of (machine pairs) - this script only READS the machine table.
PREDICTIONS (Pre-decided 132: each is a DIFFERENCE or names the step that could have fixed it):
  H   read_live x5 on one scratch: handle count RECORDED per call (measurement only; 33,987 -> 63,471 seen before).
  M1  every WhileLoop right register gets a machine left (left_of); ForLoop rights RECORDED (seed casts WhileLoop only).
  M2  S1 / rowD / m3a4: sr edge set machine == TOP-only (TOP was unique there: q_m4a_diffuid.log:90 paired 36/36).
  M3  M4a and M4b: machine pairs include 23868->23880, 23895->23909, 23469->23796; sr unpaired 0.
  C   computation_diff(S1, m3a4 / M4a / M4b) = 0 rows each (the M4a/M4b #48 row was the TOP mis-pair).
  D   diff(m3a4, M4b) nodes_added == {9996, 23459, 23469, 23796, 23844, 23874}, nodes_removed [].
  R   #23874 read_const: text '1', U32; its wire feeds #23844 'milliseconds to wait'; SR #23469/#23796 left outer wire 0.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/q_c68_srpair.log -- py -u tools/bench/q_c68_srpair.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import vigraph as V                                                                # noqa: E402
import jev_candidates as JC                                                        # noqa: E402

g, CD, DATE = K.g, K.CLAUDEDEV, time.strftime("%Y%m%d")
F = {"s1": ("D1_s1_copy.vi", "3e3d23cefd3a334001aa9d6156bf1aee"),
     "bed": ("D1_s3b_m3a3b_rowD_20260922_161040.vi", "0b84595245dd650c0e8fd3f57104782c"),
     "m3a4": ("D1_s3b_m3a4_20260923_185345.vi", "fdd6d74ac8a5ba0c1a545ad89ff2996f"),
     "m4a": ("D1_s3b_m4a_20260924_002708.vi", "bc519809937db449bc0c0ec2b6410c55"),
     "m4b": ("D1_s3b_m4b_20260924_004214.vi", "1a11d92aacabf7ec844d65b8af19f39f")}
P = dict((k, os.path.join(CD, v[0])) for k, v in F.items())
SR = lambda G: sorted((V.key_parts(a)[0], V.key_parts(b)[0]) for k, a, b, _i in G["edges"] if k == "sr")


def mloops(s, path, tag):
    loops, miss, for_ok = [], [], True
    for cls in ("ForLoop", "WhileLoop"):
        for i in range(g.count(path, cls)):
            r = g.loop_cast(path, i, cls)
            L = {"class": cls, "index": i, "loop_uid": int(r["loop_uid"]), "left_of": {},
                 "right_uids": [int(u) for u in r["shift_reg_uids"]]}
            for k, u in enumerate(L["right_uids"]):
                if cls == "ForLoop" and not for_ok:
                    miss.append(u)
                    continue
                x, err = s.safe("{0} {1}[{2}] reg {3}".format(tag, cls, i, k),
                                lambda: g.shift_reg_left(path, i, k, class_name=cls))
                if x and x.get("uid") == u and x.get("left_uids") and not x.get("errors"):
                    L["left_of"][str(u)] = [int(v) for v in x["left_uids"]]
                else:
                    miss.append(u)
                    if cls == "ForLoop":
                        for_ok = False
                        s.fact("{0}: ForLoop reg read refused ({1}) - ForLoop rights left to TOP".format(
                            tag, err or (x or {}).get("errors")))
            loops.append(L)
    s.fact("M1 {0}: {1} loops, {2} rights, {3} machine-paired, unread {4}".format(
        tag, len(loops), sum(len(L["right_uids"]) for L in loops), sum(len(L["left_of"]) for L in loops), miss))
    with open(os.path.join(K.BENCH, "graph_loops_{0}_{1}.json".format(tag, DATE)), "w", encoding="utf-8") as f:
        json.dump({"vi": P[tag], "md5": F[tag][1], "loops": loops, "unread_rights": miss,
                   "by": "q_c68_srpair (loop_cast + shift_reg_left)"}, f, indent=1)
    return loops


def main(s):
    s.start()                                         # restart FIRST (fresh=True): baseline = handles after restart
    s.discard_work()
    bp = K.mod("bench_prep")
    time.sleep(60)
    s.fact("H0 BASELINE handles 60 s after restart: {0}".format(bp.labview_handles()))
    Gr, W = JC.load(JC.BED_KEY), K.mod("wiki_build")
    for i in range(1, 6):
        W.read_live(s.work, fs_pairs=Gr["wiki"]["fs_tunnel_pairs"])
        s.fact("H{0} handles after read_live call {0} on {1}: {2}".format(i, os.path.basename(s.work), bp.labview_handles()))
    G = {}
    for tag in ("s1", "bed", "m3a4", "m4a", "m4b"):
        sc = s.work if tag == "m4b" else s.scratch(tag, source=P[tag])
        loops = mloops(s, sc, tag)
        top = [dict((k, v) for k, v in L.items() if k != "left_of") for L in loops]
        if tag in ("s1", "bed"):                      # the wiki graphs, exactly as JC.load builds them
            H = JC.load(JC.S1_KEY if tag == "s1" else JC.BED_KEY)
            part, objs, fsp = H["wiki"], list(H["objs"].values()), H["wiki"].get("fs_tunnel_pairs")
        else:                                         # the live graphs, exactly as Stage.live_graph builds them
            lv = W.read_live(sc, fs_pairs=Gr["wiki"]["fs_tunnel_pairs"])
            part, objs, fsp = {"terminals": lv["terminals"], "graph_summary": Gr["wiki"]["graph_summary"]}, lv["objs"], lv["fs_tunnel_pairs"]
        G[tag], T = [JC.from_parts(part, objs, lp, JC.node_labels_default(), fsp, tag) for lp in (loops, top)]
        m = G[tag]["method"]["sr"]
        s.fact("{0} method.sr paired {1} machine {2} top {3} unpaired {4} mismatch {5}".format(
            tag, m["paired"], m["paired_machine"], m["paired_top"], m["unpaired"], m["machine_mismatch"]))
        dm, dt = set(SR(G[tag])) - set(SR(T)), set(SR(T)) - set(SR(G[tag]))
        s.row("M2 {0} sr edges machine-only / TOP-only".format(tag), (sorted(dm), sorted(dt)), "([], []) unless M3")
        if tag in ("m4a", "m4b"):
            want = {(23868, 23880), (23895, 23909), (23469, 23796)}
            s.gate("M3 {0} machine pairs include {1}, unpaired 0".format(tag, sorted(want)),
                   want <= set(SR(G[tag])) and not m["unpaired"], sorted(p for p in SR(G[tag]) if p[0] in (23868, 23895, 23469)))
        if tag == "m4b":
            li = s.uid_index("WhileLoop", 23032, target=sc)
            for k in range(3):
                x = g.shift_reg_left(sc, li, k)
                s.fact("R SR loop #23032 reg[{0}] right #{1} out {2} inside {3} | left #{4} out(initial) {5} inside {6}".format(
                    k, x["uid"], x["out"], x["inside"], x["left"]["uid"], x["left"]["out"], x["left"]["inside"]))
            for n in (23469, 23796):
                for r in G[tag]["by_node"].get(n, []):
                    peers = [V.show(e[2] if e[1] == r["key"] else e[1]) for e in G[tag]["edges"]
                             if e[0] == "wire" and r["key"] in (e[1], e[2])]
                    s.fact("R #{0} {1} src={2} wire {3} -> peers {4}".format(n, V.show(r["key"]), r["is_source"], r["wire_uid"], peers))
            c = K.mod("build_opcreateconstonterm_v0").read_const(sc, 23874)
            s.fact("R read_const #23874: {0}".format(c))
            ks = V.terminals(G[tag], node=23844, name="milliseconds to wait", is_source=False)
            src = [V.show(x) for k in ks for x in V.sources_of(G[tag], k, kinds=("wire",))]
            s.gate("R #23844 'milliseconds to wait' is fed by #23874", any(x.startswith("#23874 ") for x in src), src)
        if sc != s.work:
            s.drop_scratch(sc)
    for a, b in (("s1", "m3a4"), ("s1", "m4a"), ("s1", "m4b")):
        cd = V.computation_diff(G[a], G[b])
        for r in cd["rows"]:
            s.fact("CDIFF({0},{1}) ROW {2}".format(a, b, dict((k, V.show(v) if k == "sink" else v) for k, v in r.items())))
        s.gate("C computation_diff({0},{1}) == 0 rows".format(a, b), not cd["rows"], "{0} rows; comp nodes +{1} -{2}".format(
            len(cd["rows"]), [x["node"] for x in cd["computation_nodes_added"]], cd["computation_nodes_removed"]))
    d = V.diff(G["m3a4"], G["m4b"])
    s.fact("DIFF(m3a4,m4b) counts {0}".format(d["counts"]))
    for k in ("nodes_added", "nodes_removed", "edges_removed", "edges_added", "changed_sinks"):
        s.fact("DIFF(m3a4,m4b) {0}: {1}".format(k, [(e[0], V.show(e[1]), V.show(e[2])) if isinstance(e, (list, tuple)) and len(e) > 2
                                                 else e for e in d[k]]))
    s.gate("D nodes_added == {9996,23459,23469,23796,23844,23874}, removed []",
           set(d["nodes_added"]) == {9996, 23459, 23469, 23796, 23844, 23874} and not d["nodes_removed"],
           (d["nodes_added"], d["nodes_removed"]))
    s.fact("HANDLES at end: {0}".format(bp.labview_handles()))


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS) + tuple((k, P[k], F[k][1]) for k in ("bed", "m3a4", "m4a", "m4b"))
    st = K.Stage(P["m4b"], F["m4b"][1], "q_c68_srpair", preload=False, deadline_min=42, reserve_s=240, pins=pins,
                 task="cycle 68: vigraph SR machine pairing, re-diff, M4b readback, read_live handle series")
    sys.exit(K.run(main, st))
