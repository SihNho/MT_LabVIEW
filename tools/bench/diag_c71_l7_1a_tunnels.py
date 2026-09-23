r"""diag_c71_l7_1a_tunnels - READ-ONLY discriminating test from archive/peer/2026-09-24-c71-l7-1a-pd3.md §4 (alternative form: never cold-load
the broken saved L7-1a file). A scratch copy of claudeDev\D1_s3_loop15.vi (1a11d92a) in a FRESH LabVIEW; ONLY the L7-1a move_in of #376 into
body #23405 (same call and position as tools/recipes/stage_d1_l7_1a.py:55); print, before and after, the terminal rows 1931, 2043, 3182, 6480,
5044, 5050, 6511 (is_source, wire_uid, term_class, node) and vigraph.diff(bed, after) half_wires_only_in_b / terminals_removed. SAVES NOTHING.
Hypothesis (b) predicts: same wire_uids as the bed; 2043 and 5050 read is_source False; their wires flagged with no source, sinks kept.
(a) cut: 2043/5050 or sinks read wire_uid 0. (c) dropped: rows absent / in terminals_removed.
PRIOR ART: stagekit.Stage (discard_work), wiki_build.read_live, jev_candidates.from_parts, vigraph.diff - unchanged; no op.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c71_l7_1a_tunnels.log -- py -u tools/bench/diag_c71_l7_1a_tunnels.py"""
import json, os, sys                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, jev_candidates as JC, vigraph as V                          # noqa: E401,E402
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
LOOPS, WIKI = J(K.BENCH, "graph_loops_m4b_20260924.json")["loops"], J(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json")
TERMS = (1931, 2043, 3182, 6480, 5044, 5050, 6511)


def lg(s, tag):
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"])
    s.fact("LIVE MAP [{0}] {1}".format(tag, lv["secs"]))
    return JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], LOOPS, JC.node_labels_default(), lv["fs_tunnel_pairs"], tag)


def rows(s, G, tag):
    out = {}
    for k, r in G["rows"].items():
        if int(r.get("term_uid") or 0) in TERMS:
            out[int(r["term_uid"])] = (r["node"], r["term_name"], r["term_class"], r["is_source"], r["wire_uid"])
    for t in TERMS:
        s.fact("TERM [{0}] {1}: {2}".format(tag, t, out.get(t, "ABSENT")))
    return out


def body(s):
    print(__doc__, flush=True); s.start(); s.discard_work()                        # noqa: E702
    B = K.mod("build_d1_v0")
    s.fact("HANDLES after open: {0!r}".format(K.mod("bench_prep").labview_handles()))
    Gb = lg(s, "bed"); rb = rows(s, Gb, "bed")                                      # noqa: E702
    wires = set(v[4] for u, v in rb.items() if u in (2043, 5050))
    for w in sorted(wires):
        s.fact("FLAG [bed] w{0}: {1}".format(w, [f for f in Gb["flags"] if f["wire_uid"] == w]))
    s.move_in(376, B.diag_index(s.work, 23405), (4760, 6765)); s.junk_purge("after move_in")  # noqa: E702
    s.gate("D0 #376 now owned by #23405", B.owner_of(s.work, 376)[1] == 23405, "")
    Ga = lg(s, "after move"); ra = rows(s, Ga, "after")                            # noqa: E702
    for w in sorted(wires | set(v[4] for u, v in ra.items() if u in (2043, 5050))):
        s.fact("FLAG [after] w{0}: {1}".format(w, [f for f in Ga["flags"] if f["wire_uid"] == w]))
    d = V.diff(Gb, Ga)
    s.fact("diff keys {0}".format(sorted(d.keys())))
    for key in ("half_wires_only_in_b", "terminals_removed", "terminals_added"):
        v = d.get(key)
        s.fact("diff {0} ({1}): {2}".format(key, len(v) if v is not None else None, v if v is None or len(v) < 60 else list(v)[:60]))
    same = all(rb.get(t, (0,) * 5)[4] == ra.get(t, (0,) * 5)[4] for t in (2043, 3182, 6480, 5050, 6511))
    s.row("wire_uids of 2043/3182/6480/5050/6511 unchanged bed -> after (hypothesis b)", same, True)
    s.row("2043 and 5050 is_source after", [ra.get(t, (None,) * 5)[3] for t in (2043, 5050)], [False, False])
    s.row("rows present after", [t for t in TERMS if t not in ra], [])
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "diag_c71_l7_1a_tunnels", preload=False, deadline_min=18, work_name="diag_c71_tun_scratch.vi",
                 pins=tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", BED, BED_MD5),))
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
