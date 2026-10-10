# ---
# labview: none
# hardware: none
# ---
r"""Card 163-a3-1 (PD396(f)): read-only facts from the adopted p5s02c graph (3d5196ab) about the K3/K4 pass-wire neighbourhood.
WHAT EXISTED FIRST: prep_c156_a1_2_measure.py measured the same ends on the P5-1 graph through stagesim; this script only READS
the p5s02c graph json (prep_c156_a1_2_lib.jload / term_brief, shared) - no sim, no plan written.
PREDICTION: graph md5 3d5196ab; #376 sits in a frame of a Case on diagram 23405 (loop 1.7 body); #5204 / #10404 exist as loop-1.7
tunnels; no shift register on 23041 carries #376 t5704/t5739 yet (K3/K4 not built). Gates: G1 md5, G2 #376 found in a case frame,
G3 #5204 and #10404 present.
Usage: py tools/bench/diag_c163_a3_1_read.py"""
import collections
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402

G = os.path.join(HERE, "graph_ring_p5s02c_20261010_131658.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("GATE %s | %s | %s" % ("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


md5 = hashlib.md5(open(G, "rb").read()).hexdigest()
gate("G1 graph md5 3d5196ab", md5.startswith("3d5196ab"), md5)
g = L.jload(G)
print("FACT keys", sorted(g.keys()), flush=True)
for k, v in g.items():
    if isinstance(v, list) and v and isinstance(v[0], dict):
        print("FACT list", k, len(v), "fields", sorted(v[0].keys()), flush=True)
T = g.get("terminals") or []
by_owner = collections.defaultdict(list)
for r in T:
    by_owner[r["owner_uid"]].append(r)
WIRE = collections.defaultdict(list)
for r in T:
    if r.get("wire_uid"):
        WIRE[r["wire_uid"]].append(r)


def show(u, tag):
    rows = by_owner.get(u, [])
    print("FACT OBJ %s #%s rows %d: %s" % (tag, u, len(rows), [(r["term_uid"], r["term_name"], r["owner_class"], r["term_class"],
                                                                 r["frame_diagram"], r.get("wire_uid")) for r in rows][:12]), flush=True)
    for r in rows:
        if r.get("wire_uid"):
            peers = [(p["term_uid"], p["term_name"], p["owner_uid"], p["owner_class"], p["frame_diagram"]) for p in WIRE[r["wire_uid"]]
                     if p is not r]
            print("FACT   wire %s from t%s -> %s" % (r["wire_uid"], r["term_uid"], peers[:6]), flush=True)
    return rows


r376 = show(376, "#376")
show(5204, "#5204")
show(10404, "#10404")
for k in ("objects", "nodes", "structures", "frames", "cases", "loops", "shift_registers", "case_frames", "mloops"):
    v = g.get(k)
    if v is None:
        continue
    hits = []
    seq = v if isinstance(v, list) else list(v.items())
    for x in seq:
        s = str(x)
        if any(t in s for t in ("23405", "23041", "'uid': 376,", "5204", "10404")):
            hits.append(s[:400])
    print("FACT %s hits %d" % (k, len(hits)), flush=True)
    for h in hits[:25]:
        print("FACT   ", h, flush=True)
fr376 = sorted(set(r["frame_diagram"] for r in r376))
gate("G2 #376 rows found (frame diagrams)", bool(r376), fr376)
# every owner whose rows sit on #376's frame diagram(s) with a selector/case tunnel class
for fd in fr376:
    owners = sorted(set((r["owner_uid"], r["owner_class"]) for r in T if r["frame_diagram"] == fd and "Tunnel" in r["owner_class"]))
    print("FACT tunnels with a face on frame %s: %s" % (fd, owners), flush=True)
    for u, c in owners:
        print("FACT   %s %s faces %s" % (u, c, [(r["term_uid"], r["term_class"], r["frame_diagram"], r.get("wire_uid")) for r in by_owner[u]]),
              flush=True)
sr = sorted(set((r["owner_uid"], r["owner_class"]) for r in T if "ShiftRegister" in r["owner_class"] and r["frame_diagram"] in (23405, 686)))
print("FACT shift-register owners with a face on 23405/686: %s" % sr, flush=True)
for u, c in sr:
    print("FACT   %s %s faces %s" % (u, c, [(r["term_uid"], r["term_class"], r["frame_diagram"], r.get("wire_uid"),
                                              [p["owner_uid"] for p in WIRE.get(r.get("wire_uid"), []) if p is not r][:4]) for r in by_owner[u]]),
          flush=True)
gate("G3 #5204 and #10404 present", bool(by_owner.get(5204)) and bool(by_owner.get(10404)))
npass = sum(1 for _l, ok in gates if ok)
print(protocol.result_line({"status": "PASS" if npass == len(gates) else "FAIL", "gates": {"pass": npass, "fail": len(gates) - npass},
                            "first_fail": next((l for l, ok in gates if not ok), None), "artefacts": []}), flush=True)
