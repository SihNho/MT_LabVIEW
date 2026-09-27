r"""selftest_stagesim_l2a1_80 - card 80-6 (PD180(a)): stagesim.op_move_in refitted to the measured L2-A1 reads. Pure Python,
no LabVIEW. Truth = tools/bench/sim/l2a1_real_80.json, reconstructed from the 80-5 tunflip run BEFORE the refit by
tools/bench/sim/l2a1_real_80_derive.py (old sim + the recorded compare; self-consistent on all 3 runs).
Base graph tools/bench/l2a1_graph_k_80.json (D1_k 6cf5b077 live read), owner map tools/bench/l2a1_facts_80.json "owners".
PREDICTIONS (contract):
  S1 closure: closure_of(5540) / (10445) = 10 nodes each, the 10 tops' union == the fixture's 28-node joint set; after the move
     every closure row off the structure's own frames sits on body 23166 and every row on its frames keeps its frame; a
     structure uid with NO owner map is REFUSED (SimError), never moved as nothing.
  S2 singles #9647 / #10247: 0 flips; edges == real, dangling == real (modulo the fixture's `either`): diff 0; the selector
     'Tunnel's #10465 / #5603 inners still read is_source True.
  S3 joint sequential move: the flipped set == the 12 measured (10 SelectorTunnel inners of #5702 #5725 #5825 #5967 #10750 +
     outers t6007/t6026), each flipped terminal's wire == the real one.
  S4 sequential: the 6 member-to-member edges the real move lost are absent; bare half-wires w5637 and w5975 deleted.
  S5 joint replay == real over all 23 recorded compare rows (0 differ) AND over the full edge/dangling sets (diff 0);
     N1 negative control: the pre-refit rule (joint, no seeds, no S2, bare kept) against the same truth gives the recorded 23;
     E1/E2 every existing selftest_stagesim* passes with its pre-refit count (stagesim selftest 0 failing gates - was 42/0, re-pinned by card 114-4; k79 4/0).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stagesim_l2a1_80.log -- py -u tools/bench/selftest_stagesim_l2a1_80.py"""
import collections, copy, json, os, re, subprocess, sys                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)  # noqa: E702
import stagesim as S, vigraph as V, jev_candidates as JC, protocol                 # noqa: E401,E402
sys.path.insert(0, HERE); import selftest_stagesim_pin as SP                       # noqa: E402,E702  card 115-1 B1
GATES, BODY = [], 23166
TOPS = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634]


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def edges(terms):                                       # stagexec.edges, copied (stagexec is LabVIEW-flagged by the hook)
    byw = collections.defaultdict(lambda: ([], []))
    for r in V.dedupe_rows(terms)[0]:
        if r["wire_uid"]:
            byw[r["wire_uid"]][0 if r["is_source"] else 1].append(r["term_uid"])
    E, dang = set(), set()
    for _w, (s, k) in byw.items():
        E.update((a, b) for a in s for b in k)
        if not s or not k:
            dang.update(s + k)
    return E, dang


def diff(st, run):
    E, D = edges(st["terminals"])
    Er, Dr, ei = set(map(tuple, run["edges"])), set(run["dangling"]), set(run["either"])
    out = {"only_sim_edges": sorted(E - Er), "only_real_edges": sorted(Er - E),
           "dangling_sim_only": sorted(D - Dr - ei), "dangling_real_only": sorted(Dr - D - ei)}
    out["n"] = sum(len(v) for v in out.values())
    return out


FX = json.load(open(os.path.join(HERE, "sim", "l2a1_real_80.json"), encoding="utf-8"))
GP = os.path.join(HERE, "l2a1_graph_k_80.json")
gr = json.load(open(GP, encoding="utf-8"))
gate("F0 fixture is l2a1_real/1 on the 80-5 graph + tunflip md5s", FX["schema"] == "l2a1_real/1" and
     FX["graph"]["md5"] == S.md5_file(GP) == "c764150c4587b78429d0bbdb9d30c27f" and
     FX["tunflip"]["md5"] == S.md5_file(os.path.join(HERE, "l2a1_tunflip_80.json")) == "578193386b5744495b1f593030210081",
     (FX["graph"]["md5"], FX["tunflip"]["md5"], S.md5_file(os.path.join(HERE, "sim", "l2a1_real_80.json"))))
CTX = {"owners": {"path": "tools/bench/l2a1_facts_80.json", "key": "owners"}}
S1g, LAB = JC.load(JC.S1_KEY), JC.node_labels_default()
P, SRC, _e, _g = S.model_for("move_in", S.load_models())
print("  FACT  move_in params {0} from {1}".format(P, SRC), flush=True)


def fresh(ctx=CTX):
    return S.base_state(copy.deepcopy(gr), ctx)


# ---------------------------------------------------------------- S1 closure
st = fresh()
c5540, d5540 = S.closure_of(st, 5540)
c10445, d10445 = S.closure_of(st, 10445)
union = set().union(*[S.closure_of(st, u)[0] for u in TOPS])
gate("S1a closure_of(#5540) and (#10445) = 10 nodes each; the 10 tops' union == the fixture's 28-node joint set",
     len(c5540) == 10 and len(c10445) == 10 and union == set(FX["runs"]["joint"]["closure_nodes"]),
     (len(c5540), len(c10445), len(union), sorted(union ^ set(FX["runs"]["joint"]["closure_nodes"]))))
eff, _c = S.op_move_in(st, {"nodes": TOPS, "dest_diagram": BODY}, P, S1g, LAB)
inner = d5540 | d10445
F0 = dict((x["term_uid"], int(x.get("frame_diagram") or 0)) for x in gr["terminals"])
bad = [(r["term_uid"], F0[r["term_uid"]], r["frame_diagram"]) for r in st["terminals"] if V.node_of(r) in union and
       r["frame_diagram"] != (F0[r["term_uid"]] if F0[r["term_uid"]] in inner else BODY)]
gate("S1b after the move: rows off the moved structures' frames on body 23166, rows on their frames keep the frame",
     not bad and eff["moved"] == sorted(union), bad[:8])
st_no = fresh({})
try:
    S.op_move_in(st_no, {"nodes": [5540], "dest_diagram": BODY}, P, S1g, LAB)
    refused = None
except S.SimError as e:
    refused = str(e)
gate("S1c a structure uid with NO owner map is refused (SimError), never moved as nothing", refused and "owners" in refused,
     refused)
print("  FACT  joint sequential: n_cut {0}, flips {1}, bare_deleted {2}".format(
    eff["n_cut"], len(eff["tunnel_flips"]), [(b["wire"], b["term_uid"]) for b in eff["bare_deleted"]]), flush=True)

# ---------------------------------------------------------------- S2 singles
for u in (9647, 10247):
    s_ = fresh()
    e_, _c = S.op_move_in(s_, {"nodes": [u], "dest_diagram": BODY}, P, S1g, LAB)
    d_ = diff(s_, FX["runs"]["single%d" % u])
    sel = [(r["term_uid"], r["is_source"]) for r in s_["terminals"] if r["owner_uid"] in (10465, 5603) and
           r["term_class"] == "InnerTerminal"]
    gate("S2 single #{0}: 0 flips, diff vs the real read 0, selector Tunnel inners still sources".format(u),
         e_["tunnel_flips"] == [] and d_["n"] == 0 and sel and all(x[1] for x in sel),
         {"flips": e_["tunnel_flips"], "diff": d_, "selector_inners": sel})

# ---------------------------------------------------------------- S3 flips
J = FX["runs"]["joint"]
fl = sorted(f["term_uid"] for f in eff["tunnel_flips"])
T1 = dict((r["term_uid"], r) for r in st["terminals"])
wires = dict((str(t), T1[t]["wire_uid"]) for t in fl)
gate("S3 joint flips == the 12 measured (10 SelectorTunnel inners + outers 6007/6026), each on the real wire",
     fl == J["flips_src_to_snk"] and wires == J["real_wire_of_flipped"] and 6007 in fl and 6026 in fl,
     {"sim": fl, "real": J["flips_src_to_snk"], "wires_sim": wires, "wires_real": J["real_wire_of_flipped"]})

# ---------------------------------------------------------------- S4 sequential + bare
E_now, _D = edges(st["terminals"])
lost = [(5634, 10256), (10253, 5608), (10594, 10259), (11052, 9680), (17365, 11059), (17487, 9676)]
bw = sorted(b["wire"] for b in eff["bare_deleted"])
gate("S4 the 6 member-to-member edges the real sequential move lost are absent; bare w5637/w5975 deleted",
     not (set(lost) & E_now) and {5637, 5975} <= set(bw), {"still_present": sorted(set(lost) & E_now), "bare_deleted": bw})

# ---------------------------------------------------------------- S5 replay == real
d = diff(st, J)
TF = json.load(open(os.path.join(HERE, "l2a1_tunflip_80.json"), encoding="utf-8"))["runs"][0]["compare"]
rows23 = [("E", tuple(x)) for x in TF["only_sim_edges"] + TF["only_real_edges"]] + \
         [("D", t) for t in TF["dangling_sim_only"] + TF["dangling_real_only"]]
_E, D_now = edges(st["terminals"])
Er, Dr = set(map(tuple, J["edges"])), set(J["dangling"])
still = [x for x in rows23 if (x[0] == "E" and ((x[1] in E_now) != (x[1] in Er))) or
         (x[0] == "D" and ((x[1] in D_now) != (x[1] in Dr)))]
gate("S5a joint replay: all {0} recorded compare rows now agree with the real read (0 differ)".format(len(rows23)),
     len(rows23) == 23 and not still, still)
gate("S5b joint replay == real over the full edge + dangling sets (diff 0)", d["n"] == 0, d)
Pold = dict(P, sequential=False, flip_moved_inputs=False, flip_needs_wired=False, bare_half_wire="keep")
s_old = fresh()
S.op_move_in(s_old, {"nodes": TOPS, "dest_diagram": BODY, "joint": True}, Pold, S1g, LAB)
dn = diff(s_old, J)
gate("N1 NEGATIVE: the pre-refit rules (joint, no moved-input seeds, no S2, bare kept) give the recorded 23 back",
     dn["n"] == 23, {k: v for k, v in dn.items() if v})
for lbl, cmd, want in (("E1 stagesim selftest", [sys.executable, "-u", os.path.join(TOOLS, "stagesim.py"), "selftest"], None),
                       ("E2 selftest_stagesim_k79", [sys.executable, "-u", os.path.join(HERE, "selftest_stagesim_k79.py")], (4, 0))):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    m = re.findall(r"=== GATES: (\d+) pass / (\d+) fail", p.stdout)
    got = tuple(int(x) for x in m[-1]) if m else None
    # card 114-4 R2: E1 was an exact-count pin (42/0) that broke each time stagesim gained gates (57, 71, 75 - all 0 fail);
    # it now asserts 0 failing stagesim gates (GATES line present, rc 0) and logs the count.
    ok = (got is not None and got[1] == 0) if want is None else got == want
    # card 115-1 B1 (review archive/peer/2026-09-28-c114d-regress.md:94-107): E1 ALSO needs pass >= the floor on record (75)
    # and every frozen label G01-G42 as a PASS line (selftest_stagesim_pin.check) - still ONE gate, so the 13/0 pin holds
    pin = SP.check(p.stdout, p.returncode) if want is None else (True, None)
    gate("{0} still passes with {1}".format(lbl, "0 failing gates, count {0}".format(got and got[0]) if want is None
                                         else "its pre-refit count {0}/{1}".format(*want)), ok and p.returncode == 0 and pin[0],
         (got, p.returncode, pin[1], [l for l in p.stdout.splitlines() if "FAIL" in l][:4]))
n_pass = sum(1 for _l, ok in GATES if ok)
first = next((l for l, ok in GATES if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(GATES) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first)))
sys.exit(0 if first is None else 1)
