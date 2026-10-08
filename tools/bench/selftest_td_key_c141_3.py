r"""selftest_td_key_c141_3 - card 141-3 pass item 2 (PD325(b)): offline test of stagekit.term_identity_gates (no LabVIEW, no COM).
REWRITTEN by card chat-T6 (PD366, docs/d1/result-gates.md): the gates now key terminals by POSITION (node, index in the node's read
order, term class, direction) and wires by their ends, so a re-used uid is INFO, never a key. Every case that still tests something
true is kept; the assertions on the removed uid-'recycled' semantics are RETIRED (listed below). stagekit is imported inside main(),
so this file declares labview: none like selftest_c147_b1_2.py (it opens no COM).
The 141-2 case is rebuilt from MEASURED files: base = graph_ring_p3b2b_20261002_133824.json (50595c62), sim end =
sim/ring_p4_s01/ring_p4_s01/step_24_wire.json, real end = the sim end relabelled with the uids the scratch log reports
(E1 PASS: real == sim at op 24, diag_c141_p4s01_scratch.log:272): owners {-1: 29407, -7: 6942, -13: 6805} (:77,:163,:249), terminal
uids of #6942 t0/t2/t3 = 28004/28296/29416 (:166-167,:180-181,:173-174), of #6805 t0/t2/t3 = 9521/28979/28985 (:252-253,:266-267,
:259-260), other new terminals fresh, new wires 6945/6978 (:275).
  T0 base graph md5 (raw or LF content - a CRLF worktree checkout changes the raw bytes only)
  T1 OLD raw-uid key on that case reproduces the logged FAIL exactly (lost 6, plan deletes 8, diff {28004, 28979}; :280)   KEPT
  T2 position key on that case: TD PASS, D PASS, 8 base keys gone; the deleted uids 28004/28979 sit on the NEW #6942/#6805 (INFO)
     REWRITTEN - RETIRED: `recycled == [28004, 28979]` (recycled is now a list of position keys: a GONE key real holds under another
     term uid; LabVIEW put these uids on new owners, which no key compares)
  T3 a kept, wired base terminal missing from real -> TD FAIL                                                              KEPT
  T4 the same loss MASKED by uid re-use (its uid given to a new terminal): OLD key PASSES (the blind spot), NEW key FAILS    KEPT
     RETIRED: `xu in recycled` (uid semantics)
  T5 a kept base terminal present but unwired in real -> TD FAIL (unwired lists its position key)                           KEPT
  T6 a new wire re-uses a lost base wire's uid: OLD D count FAILS falsely, NEW D PASSES                                      KEPT
  T7 a kept base wire lost in real (its rows unwired) -> NEW D FAILS                                                        KEPT
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_td_key_c141_3.log -- py -u tools/bench/selftest_td_key_c141_3.py"""
import copy, hashlib, json, os, sys                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
B = os.path.join(ROOT, "tools", "bench")
GR = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
SIM = os.path.join(B, "sim", "ring_p4_s01", "ring_p4_s01", "step_24_wire.json")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


def md5s(p):
    """(raw md5, LF-content md5) - a pin matches either (git worktrees checked out with core.autocrlf=true hold CRLF text)."""
    b = open(p, "rb").read()
    return hashlib.md5(b).hexdigest(), hashlib.md5(b.replace(b"\r\n", b"\n")).hexdigest()


def old_td(base, sim, real):
    """The 141-2 recipe's TD and D verbatim (stage_d1_ring_p4_s01.py:60-69 before card 141-3)."""
    wires = lambda rows: set(int(r["wire_uid"]) for r in rows if r["wire_uid"])          # noqa: E731
    bw, rw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in base), dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in real)
    gone = set(int(r["term_uid"]) for r in base) - set(int(r["term_uid"]) for r in sim)
    unw = [t for t, w_ in bw.items() if w_ and not rw.get(t) and t not in gone and any(int(r["term_uid"]) == t and r["wire_uid"] for r in sim)]
    sim_new, sim_lost = wires(sim) - wires(base), wires(base) - wires(sim)
    new, lost = wires(real) - wires(base), wires(base) - wires(real)
    return {"td_ok": not unw and set(bw) - set(rw) == gone, "lost_rows": sorted(set(bw) - set(rw)), "plan_deletes": sorted(gone), "unwired": unw,
            "d_ok": len(new) == len(sim_new) and len(lost) == len(sim_lost)}


def main():
    import protocol, stagekit as K, addrcheck as AC                                        # noqa: E401  pure functions only
    gate("T0 base graph md5 == 50595c62 (card input; raw or LF content)", "50595c62d0332a94bf066538cf20c0ae" in md5s(GR), md5s(GR))
    base = json.load(open(GR, encoding="utf-8"))["terminals"]
    st = json.load(open(SIM, encoding="utf-8"))
    sim = st.get("state", st)["terminals"]
    OWN = {-1: 29407, -7: 6942, -13: 6805}
    TU = {(6942, "array"): 28004, (6942, "new element/subarray"): 28296, (6942, "index"): 29416,
          (6805, "array"): 9521, (6805, "new element/subarray"): 28979, (6805, "index"): 28985}
    fresh, wmap, real = iter(range(900001, 900100)), {}, []
    neww = iter([6945, 6978])
    for r in sim:
        x = dict(r)
        if int(x["owner_uid"]) < 0:
            x["owner_uid"] = OWN[int(x["owner_uid"])]
            x["term_uid"] = TU.get((x["owner_uid"], x["term_name"])) or next(fresh)
        w = int(x["wire_uid"] or 0)
        if w < 0:
            if w not in wmap:
                wmap[w] = next(neww)
            x["wire_uid"] = wmap[w]
        real.append(x)
    gate("T0b reconstruction: 3 new owners x 4 terminals, 2 new wires, 6 logged uids placed",
         sum(1 for r in real if r["owner_uid"] in OWN.values()) == 12 and sorted(wmap.values()) == [6945, 6978]
         and all(any(r["term_uid"] == u and r["owner_uid"] == o for r in real) for (o, _n), u in TU.items()), sorted(wmap.items()))
    o = old_td(base, sim, real)
    gate("T1 OLD raw-uid key reproduces the logged 141-2 FAIL (lost 6 / plan deletes 8 / diff {28004, 28979}, log :280)",
         not o["td_ok"] and o["lost_rows"] == [27997, 28018, 28030, 28973, 28983, 28989]
         and o["plan_deletes"] == [27997, 28004, 28018, 28030, 28973, 28979, 28983, 28989] and o["d_ok"], o)
    n = K.term_identity_gates(base, sim, real)
    bown = dict((int(r["term_uid"]), int(r["owner_uid"])) for r in base)
    moved_uids = sorted(int(r["term_uid"]) for r in real if int(r["term_uid"]) in bown and bown[int(r["term_uid"])] != int(r["owner_uid"]))
    gate("T2 POSITION key on the 141-2 case: TD PASS, D PASS, 8 base keys gone; deleted uids on new owners (INFO) == [28004, 28979]",
         n["td_ok"] and n["d_ok"] and len(n["gone"]) == 8 and moved_uids == [28004, 28979],
         dict((k, n[k]) for k in ("td_ok", "d_ok", "recycled", "moved", "new", "lost_w")))
    pb = AC.pos_table(base)
    gone_nodes = set(k[0] for k in n["gone"])
    sw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in sim)
    X = next(r for r in base if int(r["wire_uid"] or 0) and pb[r["term_uid"]][0] not in gone_nodes and sw.get(int(r["term_uid"])) == int(r["wire_uid"]))
    xu, xk = int(X["term_uid"]), tuple(pb[X["term_uid"]])
    hit = lambda t: xk in t["lost"] or xk in t["moved"] or xk in t["unwired"]                 # noqa: E731
    r3 = [r for r in real if int(r["term_uid"]) != xu]
    n3 = K.term_identity_gates(base, sim, r3)
    gate("T3 a kept wired base terminal #{0} (key {1}) missing from real -> TD FAIL naming its key".format(xu, xk), not n3["td_ok"] and hit(n3),
         {"lost": n3["lost"][:3], "moved": n3["moved"][:3], "unwired": n3["unwired"][:3]})
    r4 = copy.deepcopy(r3)
    victim = next(r for r in r4 if r["owner_uid"] == 29407 and r["term_name"] == "output array")
    victim["term_uid"] = xu
    o4, n4 = old_td(base, sim, r4), K.term_identity_gates(base, sim, r4)
    gate("T4 loss MASKED by uid re-use (#{0} given to #29407 'output array'): OLD key blind (lost/unwired == T1's), NEW TD FAILS".format(xu),
         o4["lost_rows"] == o["lost_rows"] and o4["unwired"] == o["unwired"] == [] and not n4["td_ok"] and hit(n4),
         {"old_lost": o4["lost_rows"], "old_unw": o4["unwired"], "new": n4["td_ok"], "lost": n4["lost"][:3], "moved": n4["moved"][:3]})
    r5 = copy.deepcopy(real)
    for r in r5:
        if int(r["term_uid"]) == xu:
            r["wire_uid"] = 0
    n5 = K.term_identity_gates(base, sim, r5)
    gate("T5 kept base terminal #{0} present but unwired in real -> NEW TD FAIL (unwired lists key {1})".format(xu, xk), not n5["td_ok"] and xk in n5["unwired"], n5["unwired"][:3])
    r6 = copy.deepcopy(real)
    for r in r6:
        if int(r["wire_uid"] or 0) == 6945:
            r["wire_uid"] = 29144                                                           # a base wire the plan deletes (log :187)
    o6, n6 = old_td(base, sim, r6), K.term_identity_gates(base, sim, r6)
    gate("T6 a new wire re-uses lost base wire uid 29144: OLD D FAILS falsely, NEW D PASSES (re-use INFO)", (not o6["d_ok"]) and n6["d_ok"],
         {"old": o6["d_ok"], "reuse_noted": [y["wire"] for y in n6["reuse_noted"]]})
    W = int(X["wire_uid"])
    r7 = copy.deepcopy(real)
    for r in r7:
        if int(r["wire_uid"] or 0) == W:
            r["wire_uid"] = 0
    n7 = K.term_identity_gates(base, sim, r7)
    gate("T7 kept base wire w{0} lost in real -> NEW D FAILS".format(W), not n7["d_ok"], {"lost_w": n7["lost_w"], "sim_lost_w": n7["sim_lost_w"]})
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())
# ---
# labview: none
# hardware: none
# ---
