r"""w9635 writer probe (bench 5b, brief item 4): which EXISTING writer can re-make S1's wire 9635 =
LoopTunnel #9641 InnerTerminal '# slices in stack' (source, diagram 639) -> SelectorTunnel #9623 OuterTerminal
'# slices in stack' (sink, diagram 639). Its outer feed is w9649 from FSIT #9655 on diagram 686 (S1 graph, read
offline 2026-09-23). Each cell = a FRESH dated scratch of S1 with w9635 deleted; nothing is saved.

EXISTING WRITERS CHECKED (docs/toolkit-capabilities.md rows 54/67/68/70, stagekit.py:544-770):
  OpConnectNested_v1 - both ends by Diagram/Nodes/Terminals; a tunnel's INNER terminal is in no Nodes[] list.
  OpConnectFromWire_v0 - source = Wire(uid).Terms[i]; #9641's inner has no wire after the cut, so the only wire
     reachable is the outer feed w9649 (cells C1/C2).
  OpFsInnerTunnelConnect_v1 - casts the UID to FlatSequenceInnerTunnel (build_d1_m3a3b_d3.py:33) - a LoopTunnel
     cannot pass that cast; generalising it is a NEW op (judgement), so it is NOT a cell here.
CELLS: C1 connect_from_wire(sink = #9623 outer via its structure, src = w9649 term owned by #9641 outer)
       C2 connect_from_wire(same sink, src = w9649 SOURCE term, #9655)
       C3 connect_nested_v1(same sink, src = WhileLoop #637 on diagram 686, its '# slices in stack' terminal on w9649)
PREDICTION CONTRACT: gate per cell = the sink's new wire has source owner exactly LoopTunnel #9641, owners exactly
{#9641, #9623}, LoopTunnel count unchanged (no new tunnel), ExecState 1 (S1 is runnable; the cut makes it 0).
Predicted from prior art: C1/C3 op error or no wire, C2 a NEW LoopTunnel (T1 of OpConnectFromWire_v0 made one) ->
all three FAIL the uid gate. A PASS on any cell overturns the prediction.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/bench_map_w9635.log -- py -u tools/bench/bench_map_20260923/w9635_writers.py
"""
import json
import sys

import common as C
from common import K, g

SINK = {"uid": 9623, "term": "# slices in stack", "term_class": "OuterTerminal", "owner_class": "SelectorTunnel",
        "diagram": 639}
FEED, LOOP, PARENT = 9649, 637, 686


def sink_triple(s):
    objs = [dict(o, pos=tuple(o["pos"])) for o in g.report_all(s.work, "GObject")]
    return s.address(SINK, False, objs)


def measure(s, cell, triple, lt0):
    d, n, t = triple
    echo, rows = g.node_terms_uid(s.work, d, n)
    w = int(rows[t]["wire"] or 0)
    net = s.net_sources(w, tag="{0} sink wire".format(cell)) if w else {"source_owners": [], "all_owners": []}
    lt1, es = s.count("LoopTunnel"), s.es("{0} after write".format(cell))
    own = set(tuple(x) for x in net["all_owners"])
    ok = (net["source_owners"] == [("LoopTunnel", 9641)] and own == {("LoopTunnel", 9641), ("SelectorTunnel", 9623)}
          and lt1 == lt0 and es == 1)
    s.gate("W {0}: sink #9623 outer on a wire sourced by #9641 inner, no new tunnel, ExecState 1".format(cell), ok,
           "wire {0}; src {1}; owners {2}; LoopTunnel {3}->{4}; ES {5}".format(w, net["source_owners"], sorted(own),
                                                                             lt0, lt1, es))
    s.R.setdefault("cells", {})[cell] = {"sink_wire": w, "source_owners": net["source_owners"],
                                          "owners": sorted(own), "looptunnel": [lt0, lt1], "exec_state": es, "pass": ok}


def cell(s, name, write):
    base = s.work
    s.work = s.scratch(name)
    try:
        s.delete_wire(9635, name)
        es0, lt0 = s.es("{0} after cut".format(name)), s.count("LoopTunnel")
        s.fact("{0}: after the cut ExecState {1}, LoopTunnel {2}".format(name, es0, lt0))
        tr, how = sink_triple(s)
        s.fact("{0}: sink #9623 outer -> D/N/T {1} ({2})".format(name, tr, how))
        rec = write(s, tr)
        s.fact("{0}: writer result {1}".format(name, json.dumps(rec.get("result") if isinstance(rec, dict) else rec,
                                                                   default=str)[:400]))
        s.junk_purge(name)
        measure(s, name, tr, lt0)
    except Exception as e:                                                     # noqa: BLE001
        s.gate("W {0} ran without exception".format(name), False, "{0}: {1}".format(type(e).__name__, str(e)[:200]))
    finally:
        p, s.work = s.work, base
        s.drop_scratch(p, "H4 {0}".format(name))


def feed_index(s, want_owner=None, want_source=None):
    F = K.mod("build_opconnectfromwire_v0")
    walk = F.wire_source_owner(s.work, FEED, n=6)
    s.fact("w{0} terms: {1}".format(FEED, [(x.get("i"), x.get("owner_class"), x.get("owner_uid"), x.get("is_source"))
                                           for x in walk]))
    hit = [x for x in walk if (want_owner is None or x.get("owner_uid") == want_owner)
           and (want_source is None or bool(x.get("is_source")) == want_source)]
    return int(hit[0]["i"])


def c3(s, tr):
    didx = next(d["i"] for d in g.report_all(s.work, "Diagram") if int(d["uid"]) == PARENT)
    nidx = [r["uid"] for r in g.node_labels(s.work, didx)].index(LOOP)
    echo, rows = g.node_terms_uid(s.work, didx, nidx)
    ti = next(int(r["i"]) for r in rows if int(r["wire"] or 0) == FEED)
    s.fact("C3 source D[{0}].N[{1}] echo #{2} t{3} (the terminal carrying w{4})".format(didx, nidx, echo, ti, FEED))
    N = K.mod("build_opconnectnested_v1")
    lab = json.load(open(N.MAP_OUT, encoding="utf-8"))
    return s._op("connect_nested_v1", lambda: N.connect_nested_v1(s.work, tr[0], tr[1], tr[2], didx, nidx, ti, lab),
                 "C3")


def body(s):
    s.start()
    s.discard_work()
    cell(s, "C1", lambda s, tr: s.connect_from_wire(tr[0], tr[1], tr[2], FEED, feed_index(s, want_owner=9641)))
    cell(s, "C2", lambda s, tr: s.connect_from_wire(tr[0], tr[1], tr[2], FEED, feed_index(s, want_source=True)))
    cell(s, "C3", c3)
    s.dump()


if __name__ == "__main__":
    st = K.Stage(C.S1, C.S1_MD5, "bench_map_w9635", preload=False, deadline_min=28,
                 task="bench 5b item 4: which existing writer re-makes S1 wire 9635 (LoopTunnel inner -> SelectorTunnel outer)")
    sys.exit(K.run(body, st))
