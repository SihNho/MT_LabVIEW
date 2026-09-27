r"""selftest_stagesim_unflip_81 - card 81-5 F1: stagesim's un-flip rule (_unflip_restored_tunnels, move_in.json
`unflip_on_source`/`unflip_cascade`) against the M1 read, plus the existing stagesim self-tests unchanged. PURE PYTHON.
CASES: U1 synthetic - without the params op_wire's effect has no `unflipped` key and nothing reverts (old behaviour);
with them, a wired outer reverts the flipped inners and the cascade reverts the output tunnel's outer.
U2 the real M1 case on l2a1_graph_k_80.json + owners: sim_l2a1_81 TOPS moved one by one with the measured move_in model,
two #10170 registers wired to 6038 / 5741 (as l2a1_unflip_81.py did) -> is_source of the 15 read terminals equals
tools/bench/l2a1_unflip_81.json (run 2) after the move AND after the wire.
U3 stagesim selftest 0 failing gates (was 42/0, re-pinned by card 114-4), selftest_stagesim_k79 4/0, selftest_stagesim_l2a1_80 13/0 unchanged.
  MATERIAL=1 py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_stagesim_unflip_81.log -- py -u tools/bench/selftest_stagesim_unflip_81.py"""
import copy, json, os, re, subprocess, sys                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)  # noqa: E702
import stagesim as S, jev_candidates as JC, protocol                                   # noqa: E401,E402
sys.path.insert(0, HERE); import selftest_stagesim_pin as SP                           # noqa: E402,E702  card 115-1 B1
GATES = []
def gate(l, ok, d=""): GATES.append((l, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:900]), flush=True)  # noqa: E702,E704
J = lambda p: json.load(open(p, encoding="utf-8"))                                     # noqa: E731
T = lambda tu, ow, oc, tc, src, w, fd: {"term_uid": tu, "term_name": "", "is_source": src, "wire_uid": w, "owner_uid": ow,   # noqa: E731
                                         "owner_class": oc, "frame_diagram": fd, "term_class": tc}
PW = S.model_for("wire", S.load_models())[0]
# ---- U1 synthetic: input SelectorTunnel #10 (outer 11 sink on w1 from node #1 t1; inners 12 w2 -> #20 inner 21; 13 unwired),
#      output SelectorTunnel #20 (inner 21, outer 22 w3 -> node #30 t31)
def syn():
    return {"terminals": [T(1, 1, "Function", "Terminal", True, 1, 5), T(11, 10, "SelectorTunnel", "OuterTerminal", False, 1, 5),
                          T(12, 10, "SelectorTunnel", "InnerTerminal", True, 2, 6), T(13, 10, "SelectorTunnel", "InnerTerminal", True, 0, 7),
                          T(21, 20, "SelectorTunnel", "InnerTerminal", False, 2, 6), T(22, 20, "SelectorTunnel", "OuterTerminal", True, 3, 5),
                          T(31, 30, "Function", "Terminal", False, 3, 5), T(41, 40, "Function", "Terminal", True, 0, 5)],
            "objs": [], "loops": [], "sym": {}, "diagrams": {}, "neg": 0, "owners": {}}
for on in (False, True):
    st = syn(); reg = st.setdefault("flip_reg", {}) if on else None                       # noqa: E702
    if on:
        st["unflip"] = {"cascade": True}
    st["terminals"][0]["wire_uid"] = 0; st["terminals"][1]["wire_uid"] = 0              # noqa: E702  (the move cut w1)
    fl = S._flip_orphaned_output_tunnels(st, [], seeds=[st["terminals"][1]], needs_wired=True, reg=reg)
    eff = S.op_wire(st, {"src": {"uid": 40, "term_uid": 41}, "dst": {"uid": 10, "term_uid": 11}}, PW, None, {})[0]
    src = dict((r["term_uid"], r["is_source"]) for r in st["terminals"])
    if not on:
        gate("U1a params off: flips 12 13 22, op_wire has no `unflipped`, nothing reverts", sorted(f["term_uid"] for f in fl) == [12, 13, 22] and "unflipped" not in eff and not (src[12] or src[13] or src[22]), (fl, eff))
    else:
        gate("U1b params on: the wired outer reverts 12 13 (wired+unwired) and the cascade reverts output outer 22", sorted(u["term_uid"] for u in eff["unflipped"]) == [12, 13, 22] and src[12] and src[13] and src[22] and not src[11], eff.get("unflipped"))
# ---- U2 the M1 read
P, SRC = S.model_for("move_in", S.load_models())[:2]
gate("U2a move_in model carries unflip_on_source + unflip_cascade (measured file)", P.get("unflip_on_source") is True and P.get("unflip_cascade") is True and SRC.startswith("measured:"), SRC)
gb = dict(J(os.path.join(HERE, "l2a1_graph_k_80.json")), owners=J(os.path.join(HERE, "l2a1_facts_80.json"))["owners"])
st, LAB, S1 = S.base_state(copy.deepcopy(gb)), JC.node_labels_default(), JC.load(JC.S1_KEY)
for u in [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541]:
    S.op_move_in(st, {"nodes": [u], "dest_diagram": 23166}, P, S1, LAB)
RD = J(os.path.join(HERE, "l2a1_unflip_81.json"))["reads"]
def cmp(real):
    by = dict((r["term_uid"], r["is_source"]) for r in st["terminals"])
    return dict((int(t), (by.get(int(t)), v["is_source"])) for t, v in real.items() if by.get(int(t)) != v["is_source"])
gate("U2b after the move: is_source of the 15 read terminals == the real read", not cmp(RD["after_move"]) and len(RD["after_move"]) == 15, cmp(RD["after_move"]))
for n, (tun, t) in enumerate(((5702, 6038), (5725, 5741))):
    S.op_add_shift_reg(st, {"loop": 10170, "body": 23166, "parent": 686, "as": "U{0}".format(n)}, {}, S1, LAB)
    e = S.op_wire(st, {"src": "new:U{0}L.inner".format(n), "dst": {"uid": tun, "term_uid": t}}, PW, S1, LAB)[0]
    print("  FACT  wire -> t{0}: unflipped {1}".format(t, [(u["tunnel"], u["term_uid"]) for u in e.get("unflipped", [])]))
gate("U2c after the two register wires: is_source of the 15 read terminals == the real read (run 2)", not cmp(RD["after_wire"]) and len(RD["after_wire"]) == 15, cmp(RD["after_wire"]))
# ---- U3 existing self-tests unchanged
for lbl, cmd, want in (("stagesim selftest", [os.path.join(TOOLS, "stagesim.py"), "selftest"], None), ("selftest_stagesim_k79", [os.path.join(HERE, "selftest_stagesim_k79.py")], (4, 0)),
                       ("selftest_stagesim_l2a1_80", [os.path.join(HERE, "selftest_stagesim_l2a1_80.py")], (13, 0))):
    p = subprocess.run([sys.executable, "-u"] + cmd, capture_output=True, text=True, timeout=400)
    m = re.findall(r"=== GATES: (\d+) pass / (\d+) fail", p.stdout); got = tuple(int(x) for x in m[-1]) if m else None   # noqa: E702
    # card 114-4 R2: the stagesim pin was an exact count (42/0) that broke each time stagesim gained gates (57, 71, 75 - all
    # 0 fail); it now asserts 0 failing stagesim gates (GATES line present) and logs the count. The other two pins unchanged.
    if want is None:
        # card 115-1 B1: + rc 0, pass >= the floor on record (75), frozen G01-G42 all PASS (selftest_stagesim_pin.check)
        pin = SP.check(p.stdout, p.returncode)
        gate("U3 {0} 0 failing gates, count {1}".format(lbl, got and got[0]), got is not None and got[1] == 0 and pin[0], (got, p.returncode, pin[1]))
    else:
        gate("U3 {0} unchanged {1}/{2}".format(lbl, *want), got == want, (got, p.returncode))
n_pass = sum(1 for _l, ok in GATES if ok); first = next((l for l, ok in GATES if not ok), None)   # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(GATES) - n_pass, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first, [])))
sys.exit(0 if first is None else 1)                                                    # card 115-1 B2: rc reflects the gates
