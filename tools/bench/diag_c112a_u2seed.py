"""diag_c112a_u2seed - card 112-1, the discriminating test of archive/peer/2026-09-27-c112a-unflip81.md: does the new base-flip
seeding (stagesim.seed_base_flips_modelled, T3) change the ONE measured un-flip case? selftest_stagesim_unflip_81.py U2 replayed
with the seeding applied right after base_state; U2b/U2c compared with the real reads (l2a1_unflip_81.json). Also: what the
seeding catches on the L2-B1 bed graph (class + face counts per seeded tunnel). PURE PYTHON, no LabVIEW.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c112a_u2seed.log -- py -u tools/bench/diag_c112a_u2seed.py"""
import collections, copy, json, os, sys                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)  # noqa: E702
import stagesim as S, jev_candidates as JC, protocol                                   # noqa: E401,E402
GATES = []
def gate(l, ok, d=""): GATES.append((l, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:900]), flush=True)  # noqa: E702,E704
J = lambda p: json.load(open(p, encoding="utf-8"))                                     # noqa: E731
PW = S.model_for("wire", S.load_models())[0]
P = S.model_for("move_in", S.load_models())[0]
gb = dict(J(os.path.join(HERE, "l2a1_graph_k_80.json")), owners=J(os.path.join(HERE, "l2a1_facts_80.json"))["owners"])
st, LAB, S1 = S.base_state(copy.deepcopy(gb)), JC.node_labels_default(), JC.load(JC.S1_KEY)
seeded = S.seed_base_flips_modelled(st, S.load_models())
print("  FACT  U2 base (l2a1_graph_k_80): seeded {0} terminal(s) on tunnels {1}".format(
    len(seeded), sorted(set(f["tunnel"] for f in seeded))))
for u in [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541]:
    S.op_move_in(st, {"nodes": [u], "dest_diagram": 23166}, P, S1, LAB)
RD = J(os.path.join(HERE, "l2a1_unflip_81.json"))["reads"]
def cmp(real):
    by = dict((r["term_uid"], r["is_source"]) for r in st["terminals"])
    return dict((int(t), (by.get(int(t)), v["is_source"])) for t, v in real.items() if by.get(int(t)) != v["is_source"])
gate("U2b' WITH seeding: after the move, is_source of the 15 read terminals == the real read", not cmp(RD["after_move"]), cmp(RD["after_move"]))
for n, (tun, t) in enumerate(((5702, 6038), (5725, 5741))):
    S.op_add_shift_reg(st, {"loop": 10170, "body": 23166, "parent": 686, "as": "U{0}".format(n)}, {}, S1, LAB)
    e = S.op_wire(st, {"src": "new:U{0}L.inner".format(n), "dst": {"uid": tun, "term_uid": t}}, PW, S1, LAB)[0]
    print("  FACT  wire -> t{0}: unflipped {1}".format(t, [(u["tunnel"], u["term_uid"]) for u in e.get("unflipped", [])]))
gate("U2c' WITH seeding: after the two register wires, is_source of the 15 read terminals == the real read", not cmp(RD["after_wire"]), cmp(RD["after_wire"]))
bed = S.base_state(J(os.path.join(HERE, "graph_l2b1_20260927.json")))
sb = S.seed_base_flips_modelled(bed, S.load_models())
by = collections.defaultdict(list)
for f in sb:
    by[f["tunnel"]].append((f["side"][0], bool(f["wire"])))
cls = dict((r["owner_uid"], r["owner_class"]) for r in bed["terminals"])
for tun, faces in sorted(by.items()):
    print("  FACT  L2-B1 seeded #{0} {1}: faces (side, wired) {2}".format(tun, cls.get(tun), faces))
bare_both = [t for t, fs in by.items() if not any(w for _s, w in fs)]
print("  FACT  L2-B1 seeded tunnels with NO wired face at all (the reviewer's 'simply unwired' risk): {0}".format(sorted(bare_both)))
n_pass = sum(1 for _l, ok in GATES if ok); first = next((l for l, ok in GATES if not ok), None)   # noqa: E702
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(GATES) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first, [])))
