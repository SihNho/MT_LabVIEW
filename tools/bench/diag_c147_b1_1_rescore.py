# ---
# labview: none
# hardware: none
# offline-args: --probe
# evidence: tools/bench/cards/task_147-b1-1.json
# ---
r"""diag_c147_b1_1_rescore - card 147-b1-1 (PD356(c)): OFFLINE re-score of D / TD / PB on the STORED end read of the s06 retry scratch
(card 147-a1-8, tools/bench/diag_c147_p4s06v18_scratch.json `real_end_rows`, log tools/bench/diag_c147_p4s06v18_scratch.log :652/:657/:659),
by the PD356(b) rules. No LabVIEW, no COM call: stagekit / stagexec / vigraph / jev_candidates are imported for their PURE functions only
(term_identity_gates, wire_keys, load_final_plan, build4, computation_diff_frame, S1 graph files) - the call shapes are copied from
tools/recipes/stage_d1_ring_p4_s06v18.py:119-144 (the gate code that produced :652/:657/:659) and tools/recipes/stage_d1_l2b1.py:75-83 (PB licence).
PRIOR ART: tools/bench/selftest_td_key_c141_3.py (offline TD test); nothing re-scores a stored end read under a licence, so this file is new.

Inputs: the plan / pred / base graph exactly as the recipe loads them; the sim end = Executor.step(25)'s file via stagexec.load_final_plan; the
real end rows (5 fields) = the scratch json; full real rows for PB = the sim end rows bound to the real uids (obj binding from the run's
stagexec `bound`), overlaid with the real uid / owner / name / wire / is_source (E1 PASSED at every checkpoint, :649).
PD356(b) rules (from tools/bench/cards/brief_147-b1-1.md:13-15): TD/PB terminal key (uid, owner); a NAME change passes only for a
licensed uid. D: a plan-deleted wire uid present at the end is REUSE-NOTED only if its sources AND sinks == a sim-end wire and every sink
the sim removed is gone from the real wire. Two licence variants: L5 = the 5 measured renames, L3 = today's licence file (2832/4160/4165).

PREDICTION (from review archive/peer/2026-10-08-c147-a1-8-re1.md): R0 the reconstruction reproduces the run's gates (D 15/16 7/8, TD lost 5,
PB missing 2626|Terminal|array|0..3); under L5 D, TD, PB all PASS; under L3 TD fails on the #9503 renames (D/PB stated by the run).
--probe: print the stored JSON's structure only."""
import collections, copy, hashlib, json, os, sys                                  # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
SJ = os.path.join(BENCH, "diag_c147_p4s06v18_scratch.json")
PINS = {"tools/stagekit.py": "9a3fceaf", "tools/stagexec.py": "1bab9cf9", "tools/gscript.py": "1a80236e", "tools/elrule.py": "a5ee7d5c"}
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
GATES = []


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


GATE = gate


def fact(s):
    print("  FACT  " + s, flush=True)


def probe():
    d = J(SJ)
    for k, v in d.items():
        print(k, type(v).__name__, len(v) if hasattr(v, "__len__") else v)


# ------------------------------------------------------------------------------------------------ PD356(b) scorers
def td_356(base, sim, real, lic):
    """TD on (uid, owner): lost / gone / unwired as stagekit.term_identity_gates (stagekit.py:1383-1391) but name-free; every (uid, owner)
    whose real name != the sim end name is a RENAME, passing only when lic[uid] == owner."""
    k2 = lambda r: (int(r["term_uid"]), int(r["owner_uid"]))                     # noqa: E731
    on = lambda w: w not in (0, "", "0", "None", None)                           # noqa: E731
    bk = dict((k2(r), r) for r in base)
    sk = dict((k2(r), r) for r in sim)
    rk = dict((k2(r), r) for r in real)
    lost, gone = set(bk) - set(rk), set(bk) - set(sk)
    unw = sorted(k for k, r in bk.items() if on(r["wire_uid"]) and k not in gone and on(sk[k]["wire_uid"]) and not (k in rk and on(rk[k]["wire_uid"])))
    # TD's domain is the BASE terminals (term_identity_gates: lost/gone/unwired are base identities, stagekit.py:1377-1379); a created
    # object's terminal name is NG's business (tunnel names, recipe :117-118), so it is reported (new_obj_renames) but not scored here
    ren = sorted((k, sk[k]["term_name"], rk[k]["term_name"]) for k in set(bk) & set(sk) & set(rk) if str(sk[k]["term_name"] or "") != str(rk[k]["term_name"] or ""))
    new_ren = sorted((k, sk[k]["term_name"], rk[k]["term_name"]) for k in (set(sk) & set(rk)) - set(bk) if str(sk[k]["term_name"] or "") != str(rk[k]["term_name"] or ""))
    bad_ren = [x for x in ren if lic.get(x[0][0]) != x[0][1]]
    return {"ok": not unw and lost == gone and not bad_ren, "lost": sorted(lost), "gone": sorted(gone), "unwired": unw, "renames": ren,
            "unlicensed_renames": bad_ren, "new_obj_renames": new_ren}


def wire_keys_356(rows, lic):
    """stagekit.wire_keys (stagekit.py:1360-1371) with the source identity (uid, owner, name) where a LICENSED uid's name is replaced by '*'."""
    src = {}
    for r in rows:
        w = r.get("wire_uid") or 0
        if w in (0, "", "0", "None"):
            continue
        src.setdefault(w, set())
        if r.get("is_source"):
            u, o = int(r["term_uid"]), int(r["owner_uid"])
            src[w].add((u, o, "*" if lic.get(u) == o else str(r.get("term_name") or "")))
    return set((w, frozenset(s)) for w, s in src.items())


def wire_ends(rows, w):
    on_w = [r for r in rows if r.get("wire_uid") == w]
    return (sorted((int(r["term_uid"]), int(r["owner_uid"])) for r in on_w if r["is_source"]),
            sorted((int(r["term_uid"]), int(r["owner_uid"])) for r in on_w if not r["is_source"]))


def d_356(base, sim, real, lic, tb, ob):
    """D by PD356(b). tb maps a sim term uid to the real one (identity for base uids). Returns the counts + the reuse notes."""
    bw, sw, rw = wire_keys_356(base, lic), wire_keys_356(sim, lic), wire_keys_356(real, lic)
    new, lost, sim_new, sim_lost = rw - bw, bw - rw, sw - bw, bw - sw
    sim_del = set(k[0] for k in sim_lost) - set(k[0] for k in sw)                 # wire uids the plan deleted (absent from the sim end)
    real_w = set(k[0] for k in rw)
    notes = []
    for w in sorted(sim_del & real_w, key=str):
        rs, rk = wire_ends(real, w)
        bs, bk = wire_ends(base, w)
        match = None
        for sw_uid in set(k[0] for k in sw):
            ss, sk = wire_ends(sim, sw_uid)
            ss = sorted((tb(u), ob.get(o, o)) for u, o in ss)
            sk = sorted((tb(u), ob.get(o, o)) for u, o in sk)
            if ss == rs and sk == rk:
                match = (sw_uid, ss, sk)
        removed = sorted(set(bk) - set(match[2])) if match else None
        ok = bool(match) and not (set(removed) & set(rk))
        notes.append({"wire": w, "real_src": rs, "real_sinks": rk, "base_src": bs, "base_sinks": bk, "sim_wire": match, "sim_removed_sinks": removed,
                      "reuse_noted": ok})
    reused = set(n["wire"] for n in notes if n["reuse_noted"])
    n_new = len(new) + len(reused)                                                # a noted reuse = one lost (base) + one new (the sim wire)
    n_lost = len(lost) + len(reused)
    return {"ok": n_new == len(sim_new) and n_lost == len(sim_lost), "new": n_new, "lost": n_lost, "sim_new": len(sim_new), "sim_lost": len(sim_lost),
            "new_uids": sorted(str(k[0]) for k in new), "lost_uids": sorted(str(k[0]) for k in lost), "sim_lost_uids": sorted(str(k[0]) for k in sim_lost),
            "notes": notes}


def main():
    import stagekit as K, stagexec as SX, vigraph as V, jev_candidates as JC   # noqa: E401  pure functions only (no COM call below)
    md0 = dict((p, md5(os.path.join(ROOT, p))) for p in PINS)
    gate("P0 pins before: " + ", ".join("{0} {1}".format(os.path.basename(p), m[:8]) for p, m in md0.items()),
         all(md0[p].startswith(v) for p, v in PINS.items()))
    PLAN = os.path.join(BENCH, "plan_ring_p4_s06v18.json")
    P = J(PLAN); BASE = J(ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702  == recipe :27-28
    PRED = J(BENCH, "plan_ring_p4_s06v18_pred.json")
    _plan, steps = SX.load_final_plan(PLAN, True)                               # == Executor.__init__ (stagexec.py:1927)
    sp = steps[len(A)]
    L = J(sp if os.path.isabs(sp) else os.path.join(ROOT, sp))["state"]           # == x.step(len(A))["state"] (recipe :119)
    S = J(SJ)
    fact("inputs: scratch json {0}, base {1} md5 {2}, sim end {3} ({4} rows), real end rows {5}".format(md5(SJ)[:8], P["finalized"]["base"]["path"],
         md5(os.path.join(ROOT, P["finalized"]["base"]["path"]))[:8], sp, len(L["terminals"]), len(S["real_end_rows"])))
    RE = [dict(term_uid=a, owner_uid=b, term_name=c, wire_uid=d, is_source=e) for a, b, c, d, e in S["real_end_rows"]]
    OB = {}
    for e in S["stagexec"]:
        for k, v in (e.get("bound") or {}).items():
            OB[int(k)] = int(v)
    fact("obj binding from the run's stagexec 'bound' {0}".format(OB))

    # ---- R0: the stored rows reproduce the run's gates (stagekit.term_identity_gates, recipe :127)
    ti = K.term_identity_gates(BASE["terminals"], L["terminals"], RE)
    run = S["term_identity"]
    same = all(ti[k] == run[k] or [list(x) if isinstance(x, tuple) else x for x in ti[k]] == run[k] for k in ("new", "lost_w", "sim_new", "sim_lost_w", "lost", "unwired", "gone"))
    gate("R0 stored rows reproduce D/TD of the run: d_ok {0} new {1}/{2} lost {3}/{4}; td_ok {5} lost {6}".format(
        ti["d_ok"], len(ti["new"]), len(ti["sim_new"]), len(ti["lost_w"]), len(ti["sim_lost_w"]), ti["td_ok"], ti["lost"]), same)
    fact("D (run's key) sim_new {0}; sim_lost {1}; real new {2}; real lost {3}".format(ti["sim_new"], ti["sim_lost_w"], ti["new"], ti["lost_w"]))

    # ---- full real rows for PB: sim end rows bound to real uids, overlaid with the 5 real fields
    sim_by = dict((int(r["term_uid"]), r) for r in L["terminals"])
    re_by = dict((int(r["term_uid"]), r) for r in RE)
    TB = {}
    for u in sim_by:
        if u in re_by:
            TB[u] = u
    us = [r for u, r in sim_by.items() if u not in TB]
    ur = [r for u, r in re_by.items() if u not in set(TB.values())]
    grp = collections.defaultdict(list)
    for r in ur:
        grp[(int(r["owner_uid"]), bool(r["is_source"]))].append(r)
    for r in sorted(us, key=lambda x: -int(x["term_uid"])):
        o = OB.get(int(r["owner_uid"]), int(r["owner_uid"]))
        cand = [x for x in grp.get((o, bool(r["is_source"])), []) if int(x["term_uid"]) not in set(TB.values())]
        same_name = [x for x in cand if x["term_name"] == r["term_name"]]
        pick = (same_name or cand)
        if len(pick) >= 1:
            TB[int(r["term_uid"])] = int(sorted(pick, key=lambda x: int(x["term_uid"]))[0]["term_uid"])
    unb_s = sorted(u for u in sim_by if u not in TB)
    unb_r = sorted(set(re_by) - set(TB.values()))
    gate("R1 every sim end row binds to exactly one real end row (base uids by identity, created terms by bound owner + name)",
         not unb_s and not unb_r and len(set(TB.values())) == len(TB), "sim-only {0} real-only {1}; created-term binding {2}".format(
             unb_s[:10], unb_r[:10], dict((k, v) for k, v in TB.items() if k != v)))
    tb = lambda u: TB.get(int(u), int(u))                                         # noqa: E731
    REAL = []
    for u, r in sim_by.items():
        x = re_by[TB[u]]
        REAL.append(dict(r, term_uid=x["term_uid"], owner_uid=x["owner_uid"], term_name=x["term_name"], wire_uid=x["wire_uid"], is_source=x["is_source"]))
    diffn = sorted((int(x["term_uid"]), int(x["owner_uid"]), sim_by[u]["term_name"], x["term_name"]) for u, x in ((u, re_by[TB[u]]) for u in sim_by)
                   if str(sim_by[u]["term_name"] or "") != str(x["term_name"] or ""))
    diffo = sorted(u for u in sim_by if OB.get(int(sim_by[u]["owner_uid"]), int(sim_by[u]["owner_uid"])) != int(re_by[TB[u]]["owner_uid"]))
    fact("sim end vs real end, per bound terminal: name differs {0}; owner differs {1}".format(diffn, diffo))

    L5 = dict((int(u), int(o)) for u, o in ((2832, 2626), (4160, 2626), (4165, 2626), (9505, 9503), (9508, 9503)))
    LF = J(BENCH, "plan_ring_p4_s06v18_licence.json")
    L3 = dict((int(u), int(e["node"])) for e in LF["rename_by_uid"] for u in e["term_uids"])   # == stage_d1_l2b1.py:23
    fact("licence variants: L5 (5 measured renames) {0}; L3 (today's file, md5 {1}) {2}".format(L5, md5(os.path.join(BENCH, "plan_ring_p4_s06v18_licence.json"))[:8], L3))

    # ---- PB (recipe :137-144): S1 frame-keyed graph vs the real end graph, names restored for licensed uids (stage_d1_l2b1.py:76)
    LAB = JC.node_labels_default()
    FSPAIRS = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    objs = [dict(o, uid=OB.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
    bname = dict((int(r["term_uid"]), r["term_name"]) for r in BASE["terminals"])
    want = set((int(y["node"]), y["term"]) for y in P["open_rows"])

    def pb(rows, lic, tag):
        rows = [dict(r, term_name=bname[int(r["term_uid"])]) if lic.get(int(r["term_uid"])) == int(r["owner_uid"]) else r for r in rows]
        G1 = V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
        cd = V.computation_diff_frame(S1f, G1)
        rk = sorted(str(y["sink"]) for y in cd["rows"])
        ok = rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == want
        return ok, rk, cd, G1

    ok_sim, rk_sim, cd_sim, G_sim = pb(L["terminals"], {}, "sim")
    gate("R2 PB on the SIM end == the pred's {0} rows (the pred's own derivation)".format(len(PRED["cdiff_rows"])), ok_sim,
         {"extra": sorted(set(rk_sim) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk_sim))})
    ok_raw, rk_raw, cd_raw, G_raw = pb(REAL, {}, "raw")
    gate("R3 PB on the REAL end, no licence, reproduces the run's :659 (missing exactly 2626|Terminal|array|0..3, extra none)",
         sorted(set(PRED["cdiff_rows"]) - set(rk_raw)) == ["2626|Terminal|array|{0}".format(i) for i in range(4)] and not set(rk_raw) - set(PRED["cdiff_rows"]),
         {"extra": sorted(set(rk_raw) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk_raw))})

    # ---- PB fourth row: the #2626 keys in S1, the sim end and the real end, and their cdiff rows
    for tag, G in (("S1", S1f), ("SIM", G_sim), ("REAL", G_raw)):
        ks = sorted((k, int(r["term_uid"]), r["term_name"], r["wire_uid"]) for k, r in G["rows"].items() if V.key_parts(k)[0] == 2626 and not r["is_source"])
        fact("#2626 input keys in {0}: {1}".format(tag, ks))
    for tag, cd in (("SIM", cd_sim), ("REAL", cd_raw)):
        fact("#2626 cdiff rows vs S1 in {0}: {1}".format(tag, [(y["sink"], y["before"], y["after"]) for y in cd["rows"] if int(y["node"]) == 2626]))

    # ---- w23807
    for tag, rows in (("BASE", BASE["terminals"]), ("REAL END", RE)):
        fact("w23807 in {0}: {1}".format(tag, sorted((int(r["term_uid"]), int(r["owner_uid"]), r["term_name"], bool(r["is_source"])) for r in rows if r.get("wire_uid") == 23807)))
    sw5171 = sorted(set(r["wire_uid"] for r in L["terminals"] if int(r["term_uid"]) == 5171))
    for w in sw5171:
        fact("sim end wire {0} (the wire of source t5171): {1}".format(w, sorted((int(r["term_uid"]), int(r["owner_uid"]), r["term_name"], bool(r["is_source"]))
                                                                             for r in L["terminals"] if r.get("wire_uid") == w)))
    fact("w23807 in the sim end: {0}".format(sorted(int(r["term_uid"]) for r in L["terminals"] if r.get("wire_uid") == 23807)))

    # ---- the PD356(b) scores under both licence variants
    verdict = {}
    for name, lic in (("L5", L5), ("L3", L3)):
        td = td_356(BASE["terminals"], [dict(r, term_uid=tb(r["term_uid"]), owner_uid=OB.get(int(r["owner_uid"]), int(r["owner_uid"]))) for r in L["terminals"]], RE, lic)
        d = d_356(BASE["terminals"], L["terminals"], RE, lic, tb, OB)
        okp, rkp, _cd, _g = pb(REAL, lic, name)
        verdict[name] = (d["ok"], td["ok"], okp)
        sc = GATE if name == "L5" else (lambda label, ok, detail="": print("  SCORE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True))
        sc("{0} D (PD356(b)): new {1} == sim {2}; lost {3} == sim {4}".format(name, d["new"], d["sim_new"], d["lost"], d["sim_lost"]), d["ok"],
             {"new": d["new_uids"], "lost": d["lost_uids"], "sim_lost": d["sim_lost_uids"]})
        for n in d["notes"]:
            fact("{0} D reuse note: {1}".format(name, n))
        sc("{0} TD (PD356(b), key uid+owner): lost {1} == gone {2}; unwired {3}; unlicensed renames {4}".format(
            name, td["lost"], td["gone"], td["unwired"], td["unlicensed_renames"]), td["ok"], {"renames": td["renames"], "new_obj_renames (not TD)": td["new_obj_renames"]})
        sc("{0} PB (licensed names restored): cdiff == pred {1} rows and plan open pairs".format(name, len(PRED["cdiff_rows"])), okp,
           {"extra": sorted(set(rkp) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rkp))})
    first = next((s for s, ok in zip(("D", "TD", "PB"), verdict["L5"]) if not ok), None)
    print("VERDICT {0}; L3 (today's licence): D {1} TD {2} PB {3}".format("ALL PASS (L5)" if first is None else "L5 first failing scorer " + first,
          *["PASS" if v else "FAIL" for v in verdict["L3"]]), flush=True)
    md1 = dict((p, md5(os.path.join(ROOT, p))) for p in PINS)
    gate("P1 pins after == before: " + ", ".join("{0} {1}".format(os.path.basename(p), m[:8]) for p, m in md1.items()), md1 == md0)
    return first


if __name__ == "__main__":
    if "--probe" in sys.argv[1:]:
        probe()
        sys.exit(0)
    import protocol
    first_l5 = main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
