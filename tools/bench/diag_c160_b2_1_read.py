# ---
# labview: none
# hardware: none
# ---
"""Card 160-b2-1 throwaway reader (offline). Prints the terminal rows of the two RSR MERGE sinks (t24139, t24235) and the LSR
contrast (t24190, t24288), owners / loops entries, base_registers, and the shared route_on_state verdict on the BASE graph
for the four connects. Prediction: t24139/t24235 are InnerTerminal rows of RightShiftRegister owners, so Addr._triple skips the
SR outer branch and fails at the Nodes[] lookup; the LSR sources are wired so their routes are cfw."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as X          # noqa: E402
import vigraph as V           # noqa: E402

G = os.path.join(ROOT, "tools", "bench", "graph_ring_p5s02a_20261010_032547.json")
st = json.load(open(G))
print("KEYS", sorted(st.keys()))
T = st["terminals"]
F = ("term_uid", "owner_class", "owner_uid", "term_class", "term_name", "is_source", "wire_uid", "frame_diagram")
for tu in (24139, 24235, 24190, 24288, 3934):
    for r in [r for r in T if r["term_uid"] == tu]:
        print("ROW", dict((k, r.get(k)) for k in F), "node_of", V.node_of(r))
for reg in (24083, 24150, 24133, 24187):
    rows = [r for r in T if r["owner_uid"] == reg]
    print("REG", reg, [(r["term_uid"], r["owner_class"], r["term_class"], r["is_source"], r["wire_uid"], r["frame_diagram"]) for r in rows])
ow = st.get("owners") or {}
for d in ("23405", "31506", "31517"):
    print("OWNERS", d, ow.get(d))
for L in st.get("loops") or []:
    if set([24083, 24150, 24133, 24187]) & set(int(x) for x in (L.get("right_uids") or [])) | set(
            int(x) for v in (L.get("left_of") or {}).values() for x in (v if isinstance(v, list) else [v])):
        print("LOOP", json.dumps(L)[:600])
br = X.base_registers(st)
print("BASE_REGS", dict((k, br.get(k)) for k in (24083, 24150, 24133, 24187)))
_s, addr, loop_of, real = X.state_addr(st)
print("LOOP_OF", dict((k, loop_of.get(k)) for k in (24083, 24150, 24133, 24187)))
# who feeds the RSR sinks / who is fed by the LSR sources on the base graph
for w in (24264, 24300, 24285, 24312):
    print("WIRE", w, [(r["term_uid"], r["owner_class"], r["owner_uid"], r["term_class"], r["is_source"]) for r in T if r["wire_uid"] == w])
for src, dst in ((3934, 24139), (24190, 3934)):
    print("ROUTE_ON_STATE", src, dst, X.route_on_state(st, src, dst))
for tu in (24139, 24235):
    try:
        print("TRIPLE", tu, addr.triple(real, tu, False, loop_of))
    except X.ExecStop as e:
        print("TRIPLE", tu, "STOP", e)
d = int(next(r for r in T if r["term_uid"] == 24139)["frame_diagram"])
dl = addr.rd.diagrams()
print("DIAG", d, "idx", dl.index(d) if d in dl else None, "nodes has 24083", 24083 in addr.rd.node_uids(dl.index(d)) if d in dl else None,
      "nodes has loop", loop_of.get(24083) in addr.rd.node_uids(dl.index(d)) if d in dl else None)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None,
                              "artefacts": []}))
