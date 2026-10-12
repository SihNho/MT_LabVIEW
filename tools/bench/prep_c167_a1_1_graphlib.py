# ---
# labview: read
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/task_167-a1-1.json
# ---
r"""prep_c167_a1_1_graphlib - the whole FS-aware graph read of a LOADED VI as ONE call (card 167-a1-1, docs/script-writing.md rule 4).

Found before writing: no shared graph-read function exists (grep "def graph_read|def read_graph" tools -> 0). The block lives INLINE
in the graph diagnostics diag_c141_3..diag_c165_a3_4 _graph.py (result_166-a1-6.json:23 counts 15 copies), e.g.
tools/bench/diag_c165_a3_4_graph.py:45-83 (read_live + mloops + owner_of walk + gscript.fs_frames + stagesim.fs_measured_state).
Those stored scripts stay as the record of what ran; this module holds the same calls once, and the card 167-a1-1 diagnostic
CALLS it. Moving it into stagekit is outside this card's write globs (reported under `open`).

read_graph(s, W, fsp_path, source) -> (gr, info): gr = the graph json shape of graph_ring_p5s02e_20261012_173009.json
  {vi, md5, source, terminals, objs, loops, fs_tunnel_pairs, owners, fs_measured{fs_frames, read_err, op, borders}};
  info = {diags, owners (tuples), fsu, ff, m (fs_measured_state)}.
fs_borders(gr) -> stagesim.fs_measured_state(gr); writes gr["fs_measured"]["borders"]  (pure).
Self-test (offline, `--selftest`): fs_borders on the stored 7815af09 graph reproduces its stored borders exactly.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c167_a1_1_graphlib_selftest.log -- py -u tools/bench/prep_c167_a1_1_graphlib.py --selftest"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V, stagesim as SS                                           # noqa: E401,E402


def fs_borders(gr):
    """stagesim.fs_measured_state of a graph dict; stores its borders under gr["fs_measured"]["borders"] (str keys). Returns the
    state m. Pure. Self-test: this file's --selftest."""
    m = SS.fs_measured_state(gr)
    gr.setdefault("fs_measured", {})["borders"] = dict((str(k), v) for k, v in m["borders"].items())
    return m


def read_graph(s, W, fsp_path, source):
    """The whole FS-aware graph of the LOADED VI `W` (read_live + mloops + owner_of walk of every Diagram + gscript.fs_frames of every
    FlatSequence + fs_borders), the calls of diag_c165_a3_4_graph.py:45-83 unchanged. Returns (gr, info). Read-only on `W`.
    Self-test: the pure tail (fs_borders) in --selftest; the LabVIEW calls are those of the 15 recorded graph diags."""
    g = K.g
    fsp = json.load(open(os.path.join(ROOT, fsp_path), encoding="utf-8"))["fs_tunnel_pairs"]
    lv = K.mod("wiki_build").read_live(W, fs_pairs=fsp)
    loops, BD = K.mod("k_contract_79").mloops(s, W), K.mod("build_d1_v0")
    diags, O = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"], {}
    todo = list(diags)
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(W, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        O[u][1] and O[u][0] in V.STRUCT_OWNER and todo.append(O[u][1])                       # noqa: E701
    fsu = sorted(int(o["uid"]) for o in lv["objs"] if o["class"] == "FlatSequence")
    ff, ferr = {}, {}
    for u in fsu:
        r = s.safe("fs_frames #{0}".format(u), lambda: g.fs_frames(W, u), None)[0]
        ff[str(u)] = list((r or {}).get("frames") or [])
        ferr[str(u)] = (r or {}).get("err") if r else "read failed"
        s.fact("FS #{0}: frames {1} (terminating err {2!r})".format(u, ff[str(u)], str(ferr[str(u)])[:80]))
    gr = {"vi": W, "md5": None, "source": source, "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": fsp, "owners": dict((str(k), list(v)) for k, v in sorted(O.items())),
          "fs_measured": {"fs_frames": ff, "read_err": ferr, "op": "OpFsDiagrams_v0 via gscript.fs_frames"}}
    m = fs_borders(gr)
    return gr, {"diags": diags, "owners": O, "fsu": fsu, "ff": ff, "m": m}


def selftest():
    """Recorded case: graph_ring_p5s02e_20261012_173009.json (7815af09). fs_borders recomputed from a copy without its borders ==
    the stored borders. Prints gate lines + the C6 RESULT line; returns rc."""
    import copy
    p = os.path.join(HERE, "graph_ring_p5s02e_20261012_173009.json")
    gr = json.load(open(p, encoding="utf-8"))
    want = gr["fs_measured"]["borders"]
    g2 = copy.deepcopy(gr)
    g2["fs_measured"].pop("borders", None)
    m = fs_borders(g2)
    ok1 = g2["fs_measured"]["borders"] == want
    print("GATE {0} | T1 fs_borders(stored 7815af09 graph) == its stored borders ({1} tunnels) | {2}".format(
        "PASS" if ok1 else "FAIL", len(want), len(m["borders"])), flush=True)
    ok2 = K.md5(p).startswith("7815af09")
    print("GATE {0} | T2 the recorded graph is 7815af09 | {1}".format("PASS" if ok2 else "FAIL", K.md5(p)), flush=True)
    import protocol
    n = int(ok1) + int(ok2)
    print(protocol.result_line(protocol.make_result(n, 2 - n, None if n == 2 else ("T1" if not ok1 else "T2"), [])), flush=True)
    return 0 if n == 2 else 1


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(selftest())
