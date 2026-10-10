# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a2-1.md
# ---
r"""prep_c158_a2_1_probe - card 158-a2-1: the recorded rows the wire-0 act and its census variant need (OFFLINE, json only).
Prints, on the sim steps 15 and 16 of plan_ring_p5s02a: the source faces #24360 / #24367 and the dst terminals 5760 / 5778
(owner, class, frame), the owners entries of their frames, and connect_route's info for ops 16/17 (route_on_state, wired and wire 0).
PREDICTION: both faces on body #23405 (WhileLoop #23041); dst owner #376 on a frame whose owner is a CaseStructure.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c158_a2_1_probe.log -- py -u tools/bench/prep_c158_a2_1_probe.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

P = json.load(open(os.path.join(HERE, "plan_ring_p5s02a.json"), encoding="utf-8"))
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
n_ok = 0
for sn in (15, 16):
    s = json.load(open(STEPS[sn], encoding="utf-8"))["state"]
    print("FACT step_{0} keys {1}".format(sn, sorted(s.keys())), flush=True)
    T = s["terminals"]
    ow = s.get("owners") or {}
    for u in (24360, 24367, 5760, 5778):
        rr = [r for r in T if r["term_uid"] == u]
        for r in rr:
            print("FACT step_{0} #{1} {2} fd={3} owners[fd]={4} node_of={5}".format(sn, u, dict((k, r[k]) for k in (
                "owner_uid", "owner_class", "term_class", "term_name", "is_source", "wire_uid")), r["frame_diagram"],
                ow.get(str(int(r["frame_diagram"] or 0))), SX.V.node_of(r)), flush=True)
        n_ok += bool(rr)
    for src, dst in ((24360, 5760), (24367, 5778)):
        for z in ((), (src,)):
            k, i = SX.route_on_state(s, src, dst, zero_terms=z)
            print("FACT step_{0} route {1}->{2} zero={3}: {4} {5}".format(sn, src, dst, list(z), k, i if k == "STOP" else dict(
                (x, i.get(x)) for x in ("dst", "dst_how", "src_diag", "src_loop", "src_wire0"))), flush=True)
    # every frame diagram whose owner structure sits on body 23405 (structure rows with an OuterTerminal on 23405)
    on = sorted(set((ow.get(str(int(r["frame_diagram"] or 0))) or [None])[0] for r in T if r["owner_uid"] == 376))
    print("FACT step_{0} #376 rows' frame owners {1}".format(sn, on), flush=True)
    for fd, (cls, su) in sorted(ow.items()):
        outer = sorted(set(int(r["frame_diagram"] or 0) for r in T if r["term_class"] == "OuterTerminal"
                           and r["owner_uid"] in [x["owner_uid"] for x in T if int(x["frame_diagram"] or 0) == int(fd)
                                                  and x["term_class"] == "InnerTerminal"]))
        if cls == "CaseStructure" and 23405 in outer:
            print("FACT step_{0} case frame #{1} of CaseStructure #{2}: its tunnels' outer faces on {3}".format(sn, fd, su, outer), flush=True)
print(protocol.result_line(protocol.make_result(n_ok, 8 - n_ok, None if n_ok == 8 else "row missing", [])), flush=True)
