# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-a2-4.md
# ---
r"""diag_c153_a2_4_run - card 153-a2-4 (docs/d1/ring-p4d.md PD371(b), PD372(c)(d)): ADOPT the position-keyed vigraph (tools/vigraph.py takes the
bytes of diag_c153_b2_1_vigraph_poskey.txt a7eb58c7; old 13be0847), then measure on the adopted bytes:
 (2) the REAL PB entry point = tools/recipes/stage_d1_ring_p4_s06v18.py:142-149 (body(), inline; no shared PB function exists in stagexec /
     stage_prerun / stagekit - stagexec.e3_eval :4467 is gate E3, stage_prerun.buildarray_open_sibling :1300 is a plan lint). The recipe body
     needs LabVIEW (K.Stage), so its lines 142-149 are replayed VERBATIM on the stored s06 plan cfbd9823 + pred c1bd6b3e + licence, the stored
     adopted-s06 graph read graph_ring_p4s06_20261008_192149.json (as diag_c153_b2_1_rescore.py:22,84-87) - NO temp conversion;
 (4) compdiff_poskey, vigraph frame_80 (before AND after), t6_poskey and c147_b1_2 through a2-5's converted temp preds/plans (diag_c153_a2_5_map.json,
     the J wrapper of diag_c153_a2_5_run.py:92-95) with the ADOPTED module; (5) diag_c153_b2_1_rescore.py run unchanged (its json kept + restored).
PRIOR ART: diag_c153_a2_5_run.py (suite children copied), selftest_c153_poskey_convert.py (convert / convert_open_rows used, not copied).
PREDICTION: vf80 12/0 before and after; vigraph md5 a7eb58c7; compdiff 8/0; REAL-PB on stored files FAILS with missing == the 4 rows
'2626|Terminal|array|0..3', extra [], open pairs got 12 vs plan 13 (missing (2626,'array')), unlicensed []; the same lines with the stored pred and
open_rows converted in memory PASS and equal a2-5's temp files; t6 43/0; c147 19/1 (P0 only); rescore s06 18->14, s07 19, s08 21, s09 21, S1-s09 21;
stored plans/preds + stagekit/addrcheck/stagexec/gscript/stage_prerun/stagesim md5 unchanged. Because the recipe (not an authorised file) is
the only reader of PRED/open_rows for PB, a REAL-PB FAIL restores tools/vigraph.py 13be0847 at the end (card rule: a second file => STOP)."""
import copy, hashlib, importlib, json, os, re, shutil, subprocess, sys             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path[:0] = [HERE, TOOLS]
TXT, VG, OLD = os.path.join(HERE, "diag_c153_b2_1_vigraph_poskey.txt"), os.path.join(TOOLS, "vigraph.py"), os.path.join(HERE, "diag_c153_a2_4_vigraph_13be0847.bak")
MAPF, RJ = os.path.join(HERE, "diag_c153_a2_5_map.json"), os.path.join(HERE, "diag_c153_b2_1_rescore.json")
md5 = lambda p: hashlib.md5(open(p if os.path.isabs(p) else os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(HERE, p), encoding="utf-8"))            # noqa: E731
GATES = []


def gate(label, ok, d=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(d, default=str)[:900]), flush=True)


def realpb():
    import stagekit as K, vigraph as V, jev_candidates as JC, selftest_c153_poskey_convert as CV   # noqa: E401  adopted tools/vigraph.py
    print("  FACT  vigraph module {0} md5 {1}".format(V.__file__, md5(V.__file__)), flush=True)
    P, PRED = J("plan_ring_p4_s06v18.json"), J("plan_ring_p4_s06v18_pred.json")
    BASE, REN, LAB = J(os.path.join(ROOT, P["finalized"]["base"]["path"])), K.licence_renames(J("plan_ring_p4_s06v18_licence.json")), JC.node_labels_default()
    sf = P["finalized"]["step_files"][len(P["actions"])]
    L, GR = J(sf["path"] if os.path.isabs(sf["path"]) else os.path.join(ROOT, sf["path"]))["state"], J("graph_ring_p4s06_20261008_192149.json")
    real, FSPAIRS = GR["terminals"], BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    s1p = JC.J(JC.WIKI, JC.S1_KEY + ".json") if hasattr(JC, "J") else J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))
    # ---- stage_d1_ring_p4_s06v18.py:142-149 verbatim (be.last_objs -> the stored graph read's objs) ----
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    pbr, restored, unlic = K.pb_rename_rows(BASE["terminals"], L["terminals"], real, REN)
    G1 = V.build4(pbr, GR["objs"], copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    got = set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"])
    want = set((int(y["node"]), y["term"]) for y in P["open_rows"])
    ok = rk == PRED["cdiff_rows"] and got == want and unlic == []
    det = {"verdict": "PASS" if ok else "FAIL", "rows": [len(rk), len(PRED["cdiff_rows"])], "extra": sorted(set(rk) - set(PRED["cdiff_rows"])),
           "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "pairs": [len(got), len(want)], "pairs_extra": sorted(got - want),
           "pairs_missing": sorted(want - got), "restored": restored, "unlicensed": unlic}
    print("  FACT  REAL-PB stage_d1_ring_p4_s06v18.py:147-149 on STORED plan {0} + pred {1}: {2}".format(md5(os.path.join(HERE, "plan_ring_p4_s06v18.json"))[:8],
          md5(os.path.join(HERE, "plan_ring_p4_s06v18_pred.json"))[:8], json.dumps(det, default=str)), flush=True)
    a4 = ["2626|Terminal|array|{0}".format(i) for i in range(4)]
    gate("R1 REAL-PB result == prediction (FAIL: missing exactly the 4 #2626 array rows, extra [], open pairs 12 vs 13 missing (2626,'array'), unlicensed [])",
         not ok and det["missing"] == a4 and not det["extra"] and det["pairs_missing"] == [(2626, "array")] and not det["pairs_extra"] and unlic == [], det)
    nodes = set(int(s.split("|")[0]) for s in PRED["cdiff_rows"])
    cs = CV.sinks(CV.convert(PRED["cdiff_rows"], CV.slots(S1f, V, nodes), CV.slots(G1, V, nodes)))
    op = CV.convert_open_rows(P["open_rows"], PRED["cdiff_rows"], cs)
    M = json.load(open(MAPF, encoding="utf-8"))
    tp, tq = json.load(open(M["plan_ring_p4_s06v18_pred.json"], encoding="utf-8")), json.load(open(M["plan_ring_p4_s06v18.json"], encoding="utf-8"))
    gate("R2 the same lines with pred rows + open_rows converted IN MEMORY pass ({0} rows, {1} open) and equal a2-5's temp pred/plan".format(len(cs), len(op)),
         rk == cs and got == set((int(y["node"]), y["term"]) for y in op) and cs == tp["cdiff_rows"] and op == tq["open_rows"],
         {"extra": sorted(set(rk) - set(cs)), "missing": sorted(set(cs) - set(rk)), "eq_temp": [cs == tp["cdiff_rows"], op == tq["open_rows"]]})


def child(suite):
    if suite == "realpb":
        realpb()
    elif suite in ("compdiff", "vf80"):
        import runpy
        runpy.run_path(os.path.join(HERE, {"compdiff": "selftest_c153_compdiff_poskey.py", "vf80": "selftest_vigraph_frame_80.py"}[suite]), run_name="__main__")
        return
    else:
        M = json.load(open(MAPF, encoding="utf-8"))
        mod = importlib.import_module({"t6": "selftest_t6_poskey", "c147": "selftest_c147_b1_2"}[suite])
        orig = mod.J
        mod.J = lambda *p: orig(M[os.path.basename(os.path.join(*p))]) if os.path.basename(os.path.join(*p)) in M else orig(*p)
        mod.main()
        GATES.extend(mod.GATES)
    import protocol
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)


def run(name, argv):
    log = os.path.join(HERE, "diag_c153_a2_4_{0}.log".format(name))
    with open(log, "w", encoding="utf-8") as fh:
        rc = subprocess.run([sys.executable, "-u"] + argv, stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT, timeout=400).returncode
    txt = open(log, encoding="utf-8", errors="replace").read()
    rl = [x for x in txt.splitlines() if x.startswith("RESULT ")]
    g = json.loads(rl[-1][7:])["gates"] if rl else {"pass": -1, "fail": -1}
    f = re.findall(r"^  FAIL  (.{0,160})", txt, re.M)
    print("  FACT  {0} rc {1} -> {2}/{3}; log {4}; FAIL rows {5}".format(name, rc, g["pass"], g["fail"], os.path.relpath(log, ROOT), f), flush=True)
    return g["pass"], g["fail"], f


def main():
    gate("G0 precondition result_153-a2-5 PASS", J(os.path.join(HERE, "cards", "result_153-a2-5.json"))["status"] == "PASS")
    INV = ["tools/stagekit.py", "tools/addrcheck.py", "tools/stagexec.py", "tools/gscript.py", "tools/stage_prerun.py", "tools/stagesim.py",
           "tools/bench/graph_ring_p4s09_20261009_062044.json"] + ["tools/bench/plan_ring_p4_s0{0}v18{1}.json".format(i, x) for i in "3456" for x in ("", "_pred")]
    m0 = dict((f, md5(f)) for f in INV)
    print("  FACT  md5 before " + json.dumps(dict((os.path.basename(f), v[:8]) for f, v in m0.items())), flush=True)
    vpre = run("vf80_pre", [__file__, "--child", "vf80"])
    old = md5(VG)
    shutil.copyfile(VG, OLD)
    shutil.copyfile(TXT, VG)
    gate("A1 tools/vigraph.py adopted: old {0}, new {1} == txt a7eb58c7".format(old[:8], md5(VG)[:8]), old.startswith("13be0847") and md5(VG) == md5(TXT) == "a7eb58c7e35a134f93df168ea4cdea80")
    vpost, cc = run("vf80_post", [__file__, "--child", "vf80"]), run("compdiff", [__file__, "--child", "compdiff"])
    gate("A2 vigraph frame_80 12/0 before and after; compdiff_poskey 8/0", vpre[:2] == vpost[:2] == (12, 0) and cc[:2] == (8, 0), [vpre[:2], vpost[:2], cc[:2]])
    rp = run("realpb", [__file__, "--child", "realpb"])
    t6, c147 = run("t6", [__file__, "--child", "t6"]), run("c147", [__file__, "--child", "c147"])
    gate("A3 t6_poskey 43/0; c147_b1_2 19/1 only P0 (converted a2-5 temp preds/plans, adopted vigraph)", t6[:2] == (43, 0) and c147[:2] == (19, 1) and c147[2][0].startswith("P0 "), [t6, c147])
    bak = open(RJ, "rb").read() if os.path.exists(RJ) else None
    rs = run("rescore", [os.path.join(HERE, "diag_c153_b2_1_rescore.py")])
    shutil.copyfile(RJ, os.path.join(HERE, "diag_c153_a2_4_rescore.json"))
    if bak is not None:
        open(RJ, "wb").write(bak)
    tab = [(r["pair"][:24], r["old_rows"], r["new_rows"], r["removed"], r["added"]) for r in J("diag_c153_a2_4_rescore.json")["table"]]
    print("  FACT  rescore table (pair, old, new, removed, added): " + json.dumps(tab), flush=True)
    gate("A4 rescore old/new == s06 18/14, s07 19/19, s08 21/21, s09 21/21, S1-s09 raw 21/21; no added row; rescore {0}/{1}".format(*rs[:2]),
         [(o, n) for _, o, n, _, _ in tab] == [(18, 14), (19, 19), (21, 21), (21, 21), (21, 21)] and not any(a for *_, a in tab) and rs[1] == 0, tab)
    real_pass = '"verdict": "PASS"' in open(os.path.join(HERE, "diag_c153_a2_4_realpb.log"), encoding="utf-8", errors="replace").read()
    print("  FACT  REAL-PB verdict on stored files: {0}; realpb gates {1}/{2}".format("PASS" if real_pass else "FAIL", rp[0], rp[1]), flush=True)
    if not real_pass or rp[1] != 0 or not all(ok for _, ok in GATES):
        shutil.copyfile(OLD, VG)
        print("  FACT  REAL-PB fails on stored files (or a gate failed): tools/vigraph.py RESTORED to {0}".format(md5(VG)[:8]), flush=True)
    m1 = dict((f, md5(f)) for f in INV)
    gate("INV stored plans/preds + stage tools + s09 graph md5 after == before", m1 == m0, dict((os.path.basename(f), v[:8]) for f, v in m1.items() if v != m0[f]))
    print("  FACT  tools/vigraph.py final md5 {0}".format(md5(VG)), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        child(sys.argv[2])
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": [{"path": "tools/vigraph.py", "md5": md5(VG)}]}), flush=True)
    sys.exit(0 if not fails else 1)
