r"""diag_c100_probe2 - card 100-1, OFFLINE: loop/diagram OWNERS for the display-loop rows, and which S1-md5 graph file
carries an `owners` map (the stagesim base format of stageplan_l2a1.json = graph_k_80_owners.json).

PREDICTION: at least one tools/bench JSON with md5 3e3d23ce carries `owners`; objs has #637/#25380/#1359.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol  # noqa: E402

S1MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
npass = nfail = 0


def gate(label, ok, detail=""):
    global npass, nfail
    npass, nfail = npass + bool(ok), nfail + (not ok)
    print("GATE {0} {1} {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


cands = []
for p in sorted(glob.glob(os.path.join(HERE, "**", "*.json"), recursive=True)) + \
        sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "wiki", "subvi", "D1_s1*.json"))):
    try:
        if os.path.getsize(p) < 200000:
            continue
        with open(p, encoding="utf-8") as f:
            head = f.read(600)
        if S1MD5 not in head:
            continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict):
            cands.append((p, sorted(d.keys())))
    except Exception as e:  # noqa: BLE001
        continue
for p, k in cands:
    print("S1FILE", os.path.relpath(p, HERE), k)
withown = [p for p, k in cands if "owners" in k]
print("FACT S1-md5 graph files carrying `owners`:", withown)
base = withown[0] if withown else os.path.join(HERE, "par1359_95_graph.json")
d = json.load(open(base, encoding="utf-8"))
objs = {o["uid"]: o for o in d["objs"]}
for u in (637, 639, 686, 25380, 25392, 1359, 7911, 4866, 681, 8603, 25261, 25116, 29894):
    print("OBJ", u, objs.get(u))
own = d.get("owners") or {}
for u in (639, 686, 25392, 7911, 4866, 29894, 536):
    print("OWNER diag", u, own.get(str(u)))
for L in d.get("loops") or []:
    if L.get("loop_uid") in (637, 25380, 1359):
        print("LOOP", json.dumps(L)[:300])
# diagrams whose owner is a loop of interest; frames of the flat sequence 681
for k, v in own.items():
    if v and v[1] in (637, 25380, 1359, 681):
        print("OWNED_BY", v, "diagram", k)
# which diagram holds #637, #25380: the owner of the terminals of their bodies is the body; the loop's own
# border terminals (tunnels) sit on the outer diagram -> frame_diagram of an OuterTerminal of a tunnel of that loop
T = d["terminals"]
gk = json.load(open(os.path.join(HERE, "sim", "l2a1", "graph_k_80_owners.json"), encoding="utf-8"))["owners"]
for dg in (639, 686, 25392, 7911, 4866, 29894):
    print("K-OWNER diagram", dg, gk.get(str(dg)))
cnt = [r for r in T if r["frame_diagram"] == 7911 and r["owner_uid"] == 7911]
print("7911 body-owned rows (N/i candidates):", [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for r in cnt])
for loop, body in ((637, 639), (25380, 25392), (1359, 7911)):
    outs = sorted({r["frame_diagram"] for r in T if r["term_class"] == "OuterTerminal" and
                   any(r2["owner_uid"] == r["owner_uid"] and r2["frame_diagram"] == body for r2 in T
                       if r2["term_class"] == "InnerTerminal")})
    print("LOOP", loop, "body", body, "outer faces of its tunnels on diagrams", outs)
    kb = gk.get(str(body))
    print("FACT outer faces of #{0}: {1}; K owners[loop] = {2}".format(loop, outs, gk.get(str(loop))))
    gate("K owners[{0}] == [*, {1}]".format(body, loop), bool(kb) and kb[1] == loop, kb)
print(protocol.result_line(protocol.make_result(npass, nfail)), flush=True)
