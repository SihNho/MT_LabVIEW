# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-a2-3.md
# ---
r"""diag_c153_a2_3_run - card 153-a2-3 (docs/d1/ring-p4d.md:172-183 PD371(b), fp-70): the two PB suites against CONVERTED stored preds and the
CANDIDATE vigraph (tools/bench/diag_c153_a2_3_vigraph_cand.py = byte copy of diag_c153_b2_1_vigraph_poskey.txt a7eb58c7, put in
sys.modules['vigraph']; tools/vigraph.py is never written). PRIOR ART: selftest_t6_poskey.py:111-150 (the per-case PB pipeline is called,
not copied: T6.load / T6.enrich / K.pb_rename_rows / V.build4), selftest_c153_poskey_convert.py (the converter).
Phase 1: per t6 case, build S1 + the case graph, convert the stored pred's cdiff_rows (converter), write the result to a TEMP copy
tools/bench/<pred>_poskey_conv_<stamp>.json (mode A). Mode B (a FACT only, not a card criterion) also writes a TEMP plan copy whose
open_rows drop a (node, name) pair the conversion removed entirely - because the PB gate also compares the rows' (node, name) set with
the plan's open_rows (selftest_t6_poskey.py:149, selftest_c147_b1_2.py:122), which the card does not say to convert.
Phase 2: each suite runs in a child process: the suite module is IMPORTED unchanged, its module-level J is wrapped so a request for a
stored pred (mode B: and plan) basename loads the temp copy, then its main() and its own 3-line __main__ tail run.
PREDICTION: X1 converted pred == candidate rows in every case, X2 idempotent, X3 one conversion per pred file; compdiff 8/0;
mode A t6 38/5 and c147 17/3 (PB still FAILS on the open_rows (node, name) check: plan open (2626,'array'), candidate gives none) =
card criterion NOT met -> STOP; mode B t6 43/0, c147 19/1 (P0 only); every stored file md5 before == after."""
import copy, hashlib, importlib, importlib.util, json, os, re, shutil, subprocess, sys, time      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools")]
CAND, TXT = os.path.join(HERE, "diag_c153_a2_3_vigraph_cand.py"), os.path.join(HERE, "diag_c153_b2_1_vigraph_poskey.txt")
MAPF = os.path.join(HERE, "diag_c153_a2_3_map.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
GATES = []


def gate(label, ok, d=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(d, default=str)[:700]), flush=True)


def load_cand():
    spec = importlib.util.spec_from_file_location("vigraph", CAND)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vigraph"] = mod
    spec.loader.exec_module(mod)
    return mod


def phase1(stamp):
    V = load_cand()
    import stagekit as K, jev_candidates as JC, selftest_t6_poskey as T6, selftest_c153_poskey_convert as CV   # noqa: E401  pure functions
    LAB = JC.node_labels_default()
    s1p = T6.J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], T6.J(JC._newest("graph_objs_s1_*.json"))["objects"], T6.J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    conv, M = {}, {"A": {}, "B": {}}
    for tag, plan, rj, cmap, stored_ok in T6.CASES:
        if not os.path.exists(rj) or (stored_ok is None and "20261008_1747" not in T6.J(rj).get("work", "")):
            print("  FACT  {0} skipped (as selftest_t6_poskey.py:118)".format(tag), flush=True)
            continue
        P, BASE, L, S, ob, tb, pins = T6.load(plan, rj, cmap)
        B, SIM = BASE["terminals"], L["terminals"]
        RE, unb = T6.enrich(B, SIM, S["real_end_rows"], ob, tb)
        rows, restored, unl = K.pb_rename_rows(B, SIM, RE, None, bind={"term": tb, "obj": ob})
        objs = [dict(o, uid=ob.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
        Bg = V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs")), frame_keyed=True)
        rk = sorted(str(y["sink"]) for y in V.computation_diff_frame(S1f, Bg)["rows"])
        pname = plan.replace(".json", "_pred.json")
        stored = T6.J(T6.D, pname)["cdiff_rows"]
        nodes = set(int(s.split("|")[0]) for s in stored)
        SA, SB = CV.slots(S1f, V, nodes), CV.slots(Bg, V, nodes)
        c = CV.convert(stored, SA, SB)
        cs = CV.sinks(c)
        gate("{0} X1 converted stored pred ({1} -> {2} rows) == candidate computation_diff rows ({3})".format(tag, len(stored), len(cs), len(rk)), cs == rk,
             {"dropped": sorted(set(stored) - set(cs)), "extra_vs_cand": sorted(set(cs) - set(rk)), "missing_vs_cand": sorted(set(rk) - set(cs)),
              "changed_slots": [(r["slot"], r["name_a"], r["name_b"]) for r in c if r["name_a"] != r["name_b"]]})
        gate("{0} X2 converter idempotent on its output".format(tag), CV.sinks(CV.convert(cs, SA, SB)) == cs)
        conv.setdefault(pname, []).append((tag, cs, stored, plan))
    for pname, lst in sorted(conv.items()):
        gate("X3 {0}: every case gives the same conversion ({1})".format(pname, [t for t, _, _, _ in lst]), all(x[1] == lst[0][1] for x in lst))
        tag, cs, stored, plan = lst[0]
        PRED = T6.J(T6.D, pname)
        tp = os.path.join(HERE, pname.replace(".json", "_poskey_conv_{0}.json".format(stamp)))
        json.dump(dict(PRED, cdiff_rows=cs, poskey_conv={"card": "153-a2-3", "from_md5": md5(os.path.join(T6.D, pname))}), open(tp, "w", encoding="utf-8"), indent=1)
        M["A"][pname] = M["B"][pname] = tp
        P = T6.J(T6.D, plan)
        nm = lambda rs: set((int(s.split("|")[0]), s.split("|")[2]) for s in rs)  # noqa: E731
        gone = nm(stored) - nm(cs)
        op = [y for y in P["open_rows"] if (int(y["node"]), y["term"]) not in gone]
        tq = os.path.join(HERE, plan.replace(".json", "_poskey_conv_{0}.json".format(stamp)))
        json.dump(dict(P, open_rows=op), open(tq, "w", encoding="utf-8"), indent=1)
        M["B"][plan] = tq
        print("  FACT  {0}: temp pred {1}; mode-B temp plan {2} drops open pairs {3}".format(pname, os.path.basename(tp), os.path.basename(tq), sorted(gone)), flush=True)
    json.dump(M, open(MAPF, "w", encoding="utf-8"), indent=1)


def child(suite, mode):
    load_cand()
    if suite == "compdiff":
        import runpy
        runpy.run_path(os.path.join(HERE, "selftest_c153_compdiff_poskey.py"), run_name="__main__")
    M = json.load(open(MAPF, encoding="utf-8"))[mode]
    mod = importlib.import_module({"t6": "selftest_t6_poskey", "c147": "selftest_c147_b1_2"}[suite])
    orig = mod.J

    def J(*p):
        b = os.path.basename(os.path.join(*p))
        return orig(M[b]) if b in M else orig(*p)
    mod.J = J
    import protocol
    mod.main()
    fails = [g for g, ok in mod.GATES if not ok]                                   # the suites' own __main__ tail
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(mod.GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)


def main():
    if not os.path.exists(CAND) or md5(CAND) != md5(TXT):
        shutil.copyfile(TXT, CAND)
    gate("G1 candidate module copy md5 == txt == a7eb58c7", md5(CAND) == md5(TXT) == "a7eb58c7e35a134f93df168ea4cdea80", md5(CAND))
    FILES = ["tools/vigraph.py", "tools/stagekit.py", "tools/addrcheck.py", "tools/stagesim.py", "tools/bench/selftest_t6_poskey.py", "tools/bench/selftest_c147_b1_2.py",
             "tools/bench/selftest_c153_compdiff_poskey.py"] + ["tools/bench/plan_ring_p4_s0{0}v18{1}.json".format(i, x) for i in "3456" for x in ("", "_pred")]
    m0 = dict((f, md5(os.path.join(ROOT, f))) for f in FILES)
    print("  FACT  md5 before " + json.dumps(dict((os.path.basename(f), v[:8]) for f, v in m0.items())), flush=True)
    phase1(time.strftime("%Y%m%d_%H%M%S"))
    res = {}
    for suite, mode in (("compdiff", "A"), ("t6", "A"), ("c147", "A"), ("t6", "B"), ("c147", "B")):
        log = os.path.join(HERE, "diag_c153_a2_3_{0}_{1}.log".format(suite, mode))
        with open(log, "w", encoding="utf-8") as fh:
            rc = subprocess.run([sys.executable, "-u", __file__, "--child", suite, mode], stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT, timeout=300).returncode
        txt = open(log, encoding="utf-8", errors="replace").read()
        rl = [x for x in txt.splitlines() if x.startswith("RESULT ")]
        g = json.loads(rl[-1][7:])["gates"] if rl else {"pass": -1, "fail": -1}
        res[(suite, mode)] = (g["pass"], g["fail"], re.findall(r"^  FAIL  (.{0,160})", txt, re.M))
        print("  FACT  {0} mode {1} rc {2} -> {3}/{4}; log {5}; final: {6}; FAIL rows {7}".format(suite, mode, rc, g["pass"], g["fail"], os.path.relpath(log, ROOT),
              rl[-1][:220] if rl else "NO RESULT LINE", res[(suite, mode)][2]), flush=True)
    gate("CARD compdiff_poskey 8/0 on the candidate copy", res[("compdiff", "A")][:2] == (8, 0))
    gate("CARD t6_poskey 43/0 against converted preds", res[("t6", "A")][:2] == (43, 0), res[("t6", "A")][2])
    c = res[("c147", "A")]
    gate("CARD c147_b1_2 19/1, only P0 failing", c[:2] == (19, 1) and c[2][0].startswith("P0 "), c[2])
    m1 = dict((f, md5(os.path.join(ROOT, f))) for f in FILES)
    gate("INV every stored pred / plan / suite / stage tool md5 after == before; tools/vigraph.py 13be0847", m1 == m0 and m1["tools/vigraph.py"].startswith("13be0847"),
         dict((f, v[:8]) for f, v in m1.items() if v != m0[f]))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        child(sys.argv[2], sys.argv[3])
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": [{"path": "tools/bench/diag_c153_a2_3_map.json", "md5": md5(MAPF)}]}), flush=True)
    sys.exit(0 if not fails else 1)
