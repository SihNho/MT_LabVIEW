"""diag_c115b_r1 - card 115-2 R1 (offline, no LabVIEW): plan_l2r1.json FINAL vs B3. Gates: R1a final + end cdiff rows ==
plan_l2b3's finalized end (the 16 rows) exactly; R1b node census base -> end removes EXACTLY the 12 SR uids of
facts_c114e_inventory.json (PD228(g)); R1c no terminal of a kept node changes wire except the sole-row stubs; R1d every
step effect: no allow_either, no tunnel flip. Prints the simulated wire delta (new / lost) the stage's gate D compares."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))  # noqa: E731
PL, B3 = J(B, "plan_l2r1.json"), J(B, "plan_l2b3.json")
G = J(B, "graph_l2b3_20260928.json")
RETIRE = {9018, 9025, 29505, 29512, 1147, 1142, 5796, 5805, 119, 2972, 7311, 11001}
F = PL["finalized"]
last = J(R, F["last_step"]["path"])["state"]
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:900]), flush=True)


gate("R1a plan final, end cdiff rows == B3 finalized end (16)", PL.get("final") is True and F["end_cdiff_rows"] == B3["finalized"]["end_cdiff_rows"],
     {"n": len(F["end_cdiff_rows"]), "b3": len(B3["finalized"]["end_cdiff_rows"])})
nb = set(int(r["owner_uid"]) for r in G["terminals"])
ne = set(int(r["owner_uid"]) for r in last["terminals"])
gate("R1b node census removes exactly the retire set (12 SR uids)", nb - ne == RETIRE and not (ne - nb), {"removed": sorted(nb - ne), "added": sorted(ne - nb)})
wb = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in G["terminals"])
we = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in last["terminals"])
chg = sorted(t for t in we if we[t] != wb.get(t))
gate("R1c no kept terminal changes wire", not chg, chg[:20])
effs = []
for fn in sorted(os.listdir(os.path.join(R, os.path.dirname(F["last_step"]["path"])))):
    if fn.startswith("step_") and "delete_object" in fn:
        e = J(R, os.path.dirname(F["last_step"]["path"]), fn).get("effect") or {}
        effs.append(e)
        print("  EFFECT", fn, json.dumps(e, default=str)[:300])
gate("R1d six delete effects: no allow_either, no tunnel flip, each removes a Right+Left pair", len(effs) == 6 and all(
    not e.get("allow_either") and not e.get("tunnel_flips") and len(e.get("deleted") or []) == 2 for e in effs), len(effs))
ws = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])  # noqa: E731
print("SIM WIRES new {0} lost {1}".format(sorted(ws(last["terminals"]) - ws(G["terminals"])), sorted(ws(G["terminals"]) - ws(last["terminals"]))))
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
