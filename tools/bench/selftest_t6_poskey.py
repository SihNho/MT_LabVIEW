# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_chat-T6.md
# ---
r"""selftest_t6_poskey - card chat-T6 (docs/d1/result-gates.md): stagekit's result gates D / TD / PB keyed by POSITION (addrcheck.pos_table:
node, index in the node's read order, term class, direction), names and wire uids as report columns only. No LabVIEW, no COM.
PRIOR ART: selftest_c147_b1_2.py (load + PB reconstruction copied from it, :84-99 / :127-150), diag_c147_b1_1_rescore.py.
DATA: plans, base graphs, step files, creation maps and the stored end reads are read from the MAIN tree (MAIN below; this file
may run from a git worktree whose text files were checked out CRLF, which breaks their md5 pins). The 147-a1-8 end read (the
run that FAILED D/TD/PB on renames + a re-used wire uid, diag_c147_p4s06v18_scratch.log:652/657/659 at git 07202624) is kept
as tools/bench/fixtures/t6_s06_a1_8_end.json, because the live json was overwritten by the 147-c3 rerun.
Stored end reads keep 5 fields per row (uid, owner, name, wire, is_source) in READ order; term_class / owner_class /
frame_diagram are joined from the base row (same uid and owner) or, for a created terminal, from the sim end row bound to it
(creation map + the run's object binding; then bound owner + direction + name, as selftest_c147_b1_2.py:131-138).
PREDICTION: S0 0 per-node order differences base vs real in every batch; R0 the NAME key reproduces each run's stored verdict
(s03/s04/s05 PASS, s06 a1-8 FAIL); N1 position TD + D PASS with no licence in every batch, with and without the binding; N2 PB
PASS in every batch; M1-M6 drop / unwire / source change / index swap / class change / a new wire's source change at equal
counts each FAIL; M7-M8 selftest_c147_b1_2's T3 / T4 scenarios still FAIL; C1-C2 renaming every terminal or renumbering every
wire uid still PASS; L1 an old licence still parses and changes nothing; K2-K7 selftest_td_key_c141_3's 141-2 uid-re-use case
under the position key (K2 PASS, K3/K4/K5/K7 FAIL, K6 PASS); F1-F2 selftest_stagekit's source checks on stagekit.py.
FACT per batch: created objects whose sim-end terminal order is not LabVIEW's (why stagekit.kept_nodes)."""
import collections, copy, hashlib, json, os, sys                                  # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN = ROOT.split(os.sep + ".claude" + os.sep + "worktrees")[0]
sys.path.insert(0, os.path.join(ROOT, "tools"))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
D = os.path.join(MAIN, "tools", "bench")
CM = os.path.join(D, "creation_map")
CASES = (("s03", "plan_ring_p4_s03v18.json", os.path.join(D, "diag_c143_p4s03v18_scratch.json"), "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl", True),
         ("s04", "plan_ring_p4_s04v18.json", os.path.join(D, "diag_c144_p4s04v18_scratch.json"), "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl", True),
         ("s05", "plan_ring_p4_s05v18.json", os.path.join(D, "diag_c145_p4s05v18_scratch.json"), "plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl", True),
         ("s06-a1-8", "plan_ring_p4_s06v18.json", os.path.join(ROOT, "tools", "bench", "fixtures", "t6_s06_a1_8_end.json"),
          "plan_ring_p4_s06v18_cfbd9823_20261008_125817.jsonl", False),
         ("s06-c3", "plan_ring_p4_s06v18.json", os.path.join(D, "diag_c147_p4s06v18_scratch.json"), "plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl", None))
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def fact(s):
    print("  FACT  " + str(s)[:900], flush=True)


def load(plan, rj, cmap):
    P = J(D, plan)
    fz = P["finalized"]
    BASE = J(MAIN, fz["base"]["path"])
    sf = fz["step_files"][len(P["actions"])]
    sp = sf["path"] if os.path.isabs(sf["path"]) else os.path.join(MAIN, sf["path"])
    pins = md5(os.path.join(MAIN, fz["base"]["path"])) == fz["base"]["md5"] and md5(sp) == sf["md5"]
    L = J(sp)["state"]
    S = J(rj)
    ob, tb = {}, {}
    for e in S.get("stagexec") or []:
        ob.update((int(k), int(v)) for k, v in (e.get("bound") or {}).items())
    for line in open(os.path.join(CM, cmap), encoding="utf-8"):
        x = json.loads(line)
        if x.get("rec") == "bind":
            (ob if x["kind"] == "obj" else tb)[int(x["sim"])] = int(x["real"])
    return P, BASE, L, S, ob, tb, pins


def enrich(B, SIM, RE5, ob, tb):
    """Real rows in READ order with the fields the stored read dropped (module docstring). Returns (rows, unbound sim uids)."""
    bk = dict(((int(r["term_uid"]), int(r["owner_uid"])), r) for r in B)
    sim_by = dict((int(r["term_uid"]), r) for r in SIM)
    inv = dict((v, k) for k, v in tb.items())
    used = set(inv)
    grp = collections.defaultdict(list)
    for a, b, c, d, e in RE5:
        if (int(a), int(b)) not in bk and int(a) not in inv:
            grp[(int(b), bool(e))].append((int(a), c))
    for u, r in sorted(sim_by.items()):
        if u in sim_by and (u in tb or (u, int(r["owner_uid"])) in bk):
            continue
        cand = [x for x in grp.get((ob.get(int(r["owner_uid"]), int(r["owner_uid"])), bool(r["is_source"])), []) if x[0] not in used]
        pick = [x for x in cand if x[1] == r["term_name"]] or cand
        if pick:
            inv[sorted(pick)[0][0]] = u
            used.add(sorted(pick)[0][0])
    out = []
    for a, b, c, d, e in RE5:
        src = bk.get((int(a), int(b))) or sim_by.get(inv.get(int(a)), {})
        out.append(dict(src, term_uid=a, owner_uid=b, term_name=c, wire_uid=d, is_source=e))
    return out, sorted(set(sim_by) - set(int(r["term_uid"]) for r in B) - set(inv.values()))


def order_diffs(B, R):
    import addrcheck as AC
    tb_, tr = AC.pos_table(B), AC.pos_table(R)
    by = lambda t: dict((n, [u for u, k in sorted(t.items(), key=lambda x: x[1][1]) if k[0] == n]) for n in set(k[0] for k in t.values()))   # noqa: E731
    nb, nr = by(tb_), by(tr)
    return sorted(n for n in set(nb) & set(nr) if [u for u in nb[n] if u in set(nr[n])] != [u for u in nr[n] if u in set(nb[n])])


def names_by_node(rows, ob=None):
    """{node (mapped through ob): [(class, direction, name), ...] in read order} - the FACT on created objects."""
    import addrcheck as AC
    t, out, ob = AC.pos_table(rows), collections.defaultdict(list), ob or {}
    by = dict((r["term_uid"], r) for r in rows)
    for u, (n, i, c, s) in sorted(t.items(), key=lambda x: (str(x[1][0]), x[1][1])):
        out[ob.get(n, n)].append((c, s, by[u].get("term_name")))
    return out


def main():
    import stagekit as K, vigraph as V, jev_candidates as JC                     # noqa: E401  pure functions only
    LAB = JC.node_labels_default()
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    keep = {}
    for tag, plan, rj, cmap, stored_ok in CASES:
        if not os.path.exists(rj) or (stored_ok is None and "20261008_1747" not in J(rj).get("work", "")):
            fact("{0}: {1} absent or overwritten by a later run - skipped".format(tag, rj))
            continue
        P, BASE, L, S, ob, tb, pins = load(plan, rj, cmap)
        B, SIM = BASE["terminals"], L["terminals"]
        RE, unb = enrich(B, SIM, S["real_end_rows"], ob, tb)
        bind = {"term": tb, "obj": ob}
        gate("{0} E0 inputs md5 == plan's finalized pins; every sim end row bound to a real row ({1} rows, unbound {2})".format(tag, len(RE), unb[:6]), pins and not unb)
        od = order_diffs(B, RE)
        gate("{0} S0 base vs real end: per-node read order of the common terminals identical ({1} nodes differ)".format(tag, len(od)), not od, od[:6])
        sn, rn = names_by_node(SIM, ob), names_by_node(RE)
        co = sorted(n for n in set(ob.values()) & set(sn) & set(rn) if sn[n] != rn[n])
        fact("{0} created objects whose sim-end terminal sequence (class, direction, name) != the real read's: {1} of {2} {3}".format(
            tag, len(co), len(set(ob.values()) & set(sn) & set(rn)), [(n, sn[n][:4], rn[n][:4]) for n in co[:2]]))
        old = K.term_identity_names(B, SIM, RE)
        if stored_ok is not None:
            gate("{0} R0 the NAME key reproduces the run's stored verdict (td_ok {1}, d_ok {2}; stored {3})".format(tag, old["td_ok"], old["d_ok"], stored_ok),
                 old["td_ok"] == old["d_ok"] == stored_ok == (S["term_identity"]["td_ok"] and S["term_identity"]["d_ok"]))
        t = K.term_identity_gates(B, SIM, RE, bind=bind)
        t0 = K.term_identity_gates(B, SIM, RE)
        gate("{0} N1 position TD PASS (lost {1} == gone {2}, moved {3}, unwired {4}); D PASS (new {5}/{6}, kept-node new wires as sets {7}, lost {8}/{9} as sets) with and without bind ({10})".format(
            tag, len(t["lost"]), len(t["gone"]), t["moved"][:3], t["unwired"][:3], t["d_new"], len(t["sim_new"]), t["d_new_kept_nodes"], t["d_lost"], len(t["sim_lost_w"]), t0["d_ok"]),
            t["td_ok"] and t["d_ok"] and t0["td_ok"] and t0["d_ok"], {"renames(INFO)": t["renames"][:6], "reuse_noted(INFO)": [n["wire"] for n in t["reuse_noted"]], "extra": t["extra"][:4]})
        PRED = J(D, plan.replace(".json", "_pred.json"))
        rows, restored, unl = K.pb_rename_rows(B, SIM, RE, None, bind=bind)
        objs = [dict(o, uid=ob.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
        FSP = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
        cd = V.computation_diff_frame(S1f, V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True))
        rk = sorted(str(y["sink"]) for y in cd["rows"])
        want = set((int(y["node"]), y["term"]) for y in P["open_rows"])
        gate("{0} N2 PB (names from the sim end at the same position): cdiff == pred's {1} rows and the plan's {2} open pairs; restored {3}".format(
            tag, len(PRED["cdiff_rows"]), len(want), len(restored)), rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == want and unl == [],
            {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "restored": restored[:6]})
        keep[tag] = (B, SIM, RE, bind, t)
    tag = "s06-a1-8"
    B, SIM, RE, bind, t = keep[tag]
    import addrcheck as AC
    pb_, ps, pr = AC.pos_table(B), AC.pos_table(SIM), AC.pos_table(RE)
    kept = [r for r in RE if r["term_uid"] in pb_ and r["term_uid"] in ps and pb_[r["term_uid"]] == pr[r["term_uid"]]]
    wired = [r for r in kept if r["wire_uid"] and not r["is_source"]]
    tgt = wired[len(wired) // 2]
    M = lambda rows: K.term_identity_gates(B, SIM, rows, bind=bind)              # noqa: E731
    m1 = M([r for r in RE if r["term_uid"] != tgt["term_uid"]])
    gate("M1 drop kept wired terminal #{0} on #{1} -> TD FAILS (lost {2})".format(tgt["term_uid"], tgt["owner_uid"], m1["lost"][:2]), not m1["td_ok"])
    m2 = M([dict(r, wire_uid=0) if r["term_uid"] == tgt["term_uid"] else r for r in RE])
    gate("M2 unwire #{0} -> TD FAILS (unwired {1}) and D FAILS".format(tgt["term_uid"], m2["unwired"][:2]), not m2["td_ok"] and not m2["d_ok"])
    srcs = [r for r in kept if r["wire_uid"] and r["is_source"]]
    a = srcs[len(srcs) // 2]
    c = next(r for r in kept if not r["wire_uid"] and r["is_source"] and r["owner_uid"] != a["owner_uid"])
    rows3 = [dict(r, wire_uid=a["wire_uid"]) if r["term_uid"] == c["term_uid"] else dict(r, wire_uid=0) if r["term_uid"] == a["term_uid"] else r for r in RE]
    m3 = M(rows3)
    m3c = K.term_identity_gates(B, SIM, rows3)
    gate("M3 wire {0}'s source moved #{1} -> #{2} -> D FAILS with bind ({3}) and without ({4})".format(a["wire_uid"], a["term_uid"], c["term_uid"], m3["d_ok"], m3c["d_ok"]),
         not m3["d_ok"] and not m3c["d_ok"])
    kn = K.kept_nodes(K._pos_rows(B), t["gone"])
    nw = [w for w in t["new"] if all(pr[r["term_uid"]][0] in kn for r in RE if str(r["wire_uid"]) == w)]
    a2 = next(r for r in RE if str(r["wire_uid"]) == nw[0] and r["is_source"])
    c2 = next(r for r in kept if not r["wire_uid"] and r["is_source"] and r["owner_uid"] != a2["owner_uid"] and pr[r["term_uid"]][0] in kn)
    m6 = M([dict(r, wire_uid=a2["wire_uid"]) if r["term_uid"] == c2["term_uid"] else dict(r, wire_uid=0) if r["term_uid"] == a2["term_uid"] else r for r in RE])
    gate("M6 NEW wire {0} (kept nodes only) gets source #{1} instead of #{2}: counts still equal ({3}/{4}) -> D FAILS on the set".format(
        a2["wire_uid"], c2["term_uid"], a2["term_uid"], m6["d_new"], len(m6["sim_new"])), not m6["d_ok"])
    nodes = collections.defaultdict(list)
    for i, r in enumerate(RE):
        if r["term_uid"] in pb_ and not r["wire_uid"]:
            nodes[(pr[r["term_uid"]][0], r.get("term_class"), bool(r["is_source"]))].append(i)
    i, j = next(v for v in nodes.values() if len(v) >= 2)[:2]
    rows4 = list(RE)
    rows4[i], rows4[j] = rows4[j], rows4[i]
    m4 = M(rows4)
    gate("M4 swap two UNWIRED same-class terminals #{0}/#{1} of node #{2} in read order -> TD FAILS (moved {3})".format(RE[i]["term_uid"], RE[j]["term_uid"], pr[RE[i]["term_uid"]][0], m4["moved"][:2]),
         not m4["td_ok"] and m4["moved"])
    m5 = M([dict(r, term_class="Changed") if r["term_uid"] == tgt["term_uid"] else r for r in RE])
    gate("M5 term class of #{0} changed -> TD FAILS".format(tgt["term_uid"]), not m5["td_ok"])
    m7 = M([dict(r, wire_uid=23807, is_source=False) if int(r["term_uid"]) == 9519 else r for r in RE])
    gate("M7 (selftest_c147_b1_2 T3) re-used w23807 also keeps the sink 9519 the plan removed -> D FAILS", not m7["d_ok"])
    m8 = M([dict(r, owner_uid=9503) if int(r["term_uid"]) == 2832 else r for r in RE])
    gate("M8 (selftest_c147_b1_2 T4) renamed #2832 also changes owner 2626 -> 9503 -> TD FAILS", not m8["td_ok"])
    c1 = M([dict(r, term_name="renamed_" + str(r["term_uid"])) for r in RE])
    gate("C1 every real terminal renamed -> TD and D still PASS ({0} renames reported as INFO)".format(len(c1["renames"])), c1["td_ok"] and c1["d_ok"] and len(c1["renames"]) > 1000)
    c2 = M([dict(r, wire_uid=(r["wire_uid"] + 900000) if r["wire_uid"] else 0) for r in RE])
    gate("C2 every real wire uid renumbered -> D still PASS", c2["d_ok"] and c2["td_ok"])
    lic = K.licence_renames(J(D, "plan_ring_p4_s06v18_licence.json"))
    l1 = K.term_identity_gates(B, SIM, RE, renames=lic, bind=bind)
    gate("L1 the s06 licence still parses ({0} renames) and only echoes: verdict unchanged".format(len(lic or {})),
         lic and len(lic) == 5 and l1["td_ok"] == t["td_ok"] and l1["d_ok"] == t["d_ok"] and len(l1["licence_renames_listed"]) == 5)
    k141(K)
    import ast
    src = open(os.path.join(ROOT, "tools", "stagekit.py"), encoding="utf-8").read()
    bad = ["line {0}".format(nd.lineno) for nd in ast.walk(ast.parse(src)) if isinstance(nd, ast.BinOp) and isinstance(nd.op, ast.Mod)
           and isinstance(getattr(nd, "left", None), (ast.Constant, ast.JoinedStr)) and (not isinstance(nd.left, ast.Constant) or isinstance(nd.left.value, str))]
    gate("F1 stagekit builds no message with the `%` operator (selftest_stagekit.py:150-163)", not bad, bad[:3])
    gate("F2 stagekit's own source carries no bold-FAIL marker", ("*" * 2 + "FAIL" + "*" * 2) not in src.replace("`" + "*" * 2 + "FAIL" + "*" * 2 + "`", ""))


def k141(K):
    """selftest_td_key_c141_3.py's 141-2 case (P4 s01 scratch: LabVIEW re-used deleted uids), rebuilt exactly as there (:40-62), re-asked
    under the POSITION key - that file declares labview: read (it imports stagekit at top level), so this card (labview none) cannot launch it."""
    GR = os.path.join(D, "graph_ring_p3b2b_20261002_133824.json")
    SP = os.path.join(D, "sim", "ring_p4_s01", "ring_p4_s01", "step_24_wire.json")
    base = J(GR)["terminals"]
    st = J(SP)
    sim = st.get("state", st)["terminals"]
    OWN = {-1: 29407, -7: 6942, -13: 6805}
    TU = {(6942, "array"): 28004, (6942, "new element/subarray"): 28296, (6942, "index"): 29416,
          (6805, "array"): 9521, (6805, "new element/subarray"): 28979, (6805, "index"): 28985}
    fresh, wmap, real, neww = iter(range(900001, 900100)), {}, [], iter([6945, 6978])
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
    n = K.term_identity_gates(base, sim, real)
    gate("K2 141-2 case (deleted uids 28004/28979 re-used on new #6942/#6805): position TD PASS, D PASS, 8 base keys gone",
         n["td_ok"] and n["d_ok"] and len(n["gone"]) == 8, dict((k, n[k]) for k in ("recycled", "moved", "new", "lost_w")))
    gone_n = set(k[0] for k in n["gone"])
    sw = dict((int(r["term_uid"]), int(r["wire_uid"] or 0)) for r in sim)
    X = next(r for r in base if int(r["wire_uid"] or 0) and int(r["owner_uid"]) not in gone_n and sw.get(int(r["term_uid"])) == int(r["wire_uid"]))
    xu = int(X["term_uid"])
    r3 = [r for r in real if int(r["term_uid"]) != xu]
    gate("K3 kept wired base terminal #{0} missing from real -> TD FAILS".format(xu), not K.term_identity_gates(base, sim, r3)["td_ok"])
    r4 = copy.deepcopy(r3)
    next(r for r in r4 if r["owner_uid"] == 29407 and r["term_name"] == "output array")["term_uid"] = xu
    gate("K4 the same loss MASKED by uid re-use (#{0} given to #29407 'output array') -> TD still FAILS".format(xu), not K.term_identity_gates(base, sim, r4)["td_ok"])
    r5 = [dict(r, wire_uid=0) if int(r["term_uid"]) == xu else r for r in real]
    n5 = K.term_identity_gates(base, sim, r5)
    gate("K5 kept base terminal #{0} present but unwired -> TD FAILS (unwired {1})".format(xu, n5["unwired"][:2]), not n5["td_ok"] and n5["unwired"])
    r6 = [dict(r, wire_uid=29144) if int(r["wire_uid"] or 0) == 6945 else r for r in real]
    gate("K6 a new wire re-uses the deleted base wire uid 29144 -> D PASSES", K.term_identity_gates(base, sim, r6)["d_ok"])
    W = int(X["wire_uid"])
    r7 = [dict(r, wire_uid=0) if int(r["wire_uid"] or 0) == W else r for r in real]
    gate("K7 kept base wire w{0} lost in real -> D FAILS".format(W), not K.term_identity_gates(base, sim, r7)["d_ok"])


if __name__ == "__main__":
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
