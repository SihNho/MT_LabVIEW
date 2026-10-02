r"""launch_p3b2_resume_c135 - card 135-2 pass 5 (PD294(d)): the RESUME runner of RING P3b-2 from the launch's in-between file
(session a ACCEPTED, PD294(a)) - WRITTEN, NOT LAUNCHED (the launch is card 135-3). NO finalize branch (PD294(c)).
CHAIN (live, `--launch`): L0 no LabVIEW; pins (recipe b, plan b ae6b6111, graphs 123012 / 102553); a-file 49cf7f77 + bed 9d7bf287
md5; C offline compare 123012 vs 102553, both re-annotated (launch_p3b2_resume_c135_compare.compare) - DIFFERENT => STOP; C2
stage_prerun.check_launch(recipe b) ALLOW; state file a_file/a_md5 written for the children -> B session b on the a-file (child
launch_p3b2_c135_b.py, nested bgrun 45 min) -> B2 LabVIEW gone, bed + a-file unchanged -> E FULL final Error List (child
launch_p3b2_c135_el.py = --role final) -> E2 total in 49..52, E3 classes in lo..hi of errorlist_expect_p3b2ab.json -> E4 gone.
WHAT EXISTED (reused, unchanged): launch_p3b2_c135.py's executors Live / Dry (nested bgrun children, taskkill/tasklist pair, the
dry fixtures) and its B and E gate formulas; its children _b.py / _el.py read launch_p3b2_c135_state.json. Not on stagekit.Stage:
this runner opens no LabVIEW itself, and an `import stagekit` would make its --dry a LabVIEW run under a labview:none card (fp-30's
class, protocol.py:385).
PREDICTION (live): C EQUAL (diag_c135_2_compare.log); B peak <= 690 (scratch b +56.5 over its start) and <= X10 + 10; E total 49..52,
loose ends 22 -> 20, classes in lo..hi; bed + a-file unchanged. --dry: every gate PASS on the stubs, nothing spawned or written.
    py tools/bgrun.py --material --max-min 120 --log tools/bench/launch_p3b2_resume_c135.log -- py -u tools/bench/launch_p3b2_resume_c135.py --launch"""
import json, os, re, sys                                                           # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
sys.path.insert(0, B)
import protocol as P                                                               # noqa: E402
import launch_p3b2_c135 as L                                                       # noqa: E402
import launch_p3b2_resume_c135_compare as CMP                                      # noqa: E402
NEW_G, NEW_G_MD5 = "tools/bench/graph_ring_p3b2a_fs_20261002_123012.json", "d0a32178a87b2c9593b0d0773d332215"
AFILE = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b2a_20261002_122043.vi"
AMD5 = "49cf7f770fc331e06607687af640ad5e"
PINS = {L.RB: L.PINS[L.RB], L.PB: "ae6b6111d766a4ba27d0695f29958c23", L.REF_GRAPH: L.PINS[L.REF_GRAPH], NEW_G: NEW_G_MD5}


def run(X):
    import stage_prerun as SP
    gates, arts, started = [], [], []

    def gate(name, ok, det=""):
        gates.append((name, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)
        return bool(ok)

    def stop():
        started and X.labview_gone(kill=True)                                     # noqa: E701 - only after OUR child ran
        return gates, arts
    if not gate("L0c no LabVIEW running before the chain", X.labview_gone(kill=False)):
        return stop()
    got = dict((p, L.md5(os.path.join(L.ROOT, p))) for p in PINS)
    if not gate("L0a pins: recipe b, plan b ae6b6111, graphs 123012 + 102553", got == PINS, dict((p, m) for p, m in got.items() if m != PINS[p])):
        return stop()
    if not gate("L0b a-file {0} + bed {1} md5 (read-only)".format(AMD5[:8], L.BED_MD5[:8]),
                os.path.exists(AFILE) and L.md5(AFILE) == AMD5 and L.md5(L.BED) == L.BED_MD5):
        return stop()
    eq, diff, ch = CMP.compare(L.J(NEW_G), L.J(L.REF_GRAPH))
    print("  FACT  C re-annotation changes new {0} / ref {1}".format(ch["n_new"], ch["n_ref"]), flush=True)
    if not gate("C compare 123012 vs 102553 (both re-annotated, strict) EQUAL - DIFFERENT stops (no finalize branch)", eq, diff):
        return stop()
    ok, why = SP.check_launch(L.recipe_cmd(L.RB))
    if not gate("C2 check_launch({0}) ALLOW on plan b ae6b6111".format(os.path.basename(L.RB)), ok, why.replace("\n", " | ")):
        return stop()
    X.write(L.STATE, {"a_file": AFILE, "a_md5": AMD5, "graph": NEW_G, "graph_md5": NEW_G_MD5, "compare": "EQUAL", "resume": "launch_p3b2_resume_c135"})
    started.append("B")
    rc, seg = X.child("B")
    sb = X.mem.get("b") if X.dry else (L.J(os.path.join(B, "launch_p3b2_c135_b_sum.json")) if os.path.exists(os.path.join(B, "launch_p3b2_c135_b_sum.json")) else {})
    bfile, bmd5, pk, x10 = sb.get("final"), sb.get("final_md5"), sb.get("peak_mb"), sb.get("x10")
    ok = rc == 0 and bfile and (X.dry or (os.path.exists(bfile) and L.md5(bfile) == bmd5)) and pk is not None and x10 and pk <= 690.0 and pk <= x10 + 10
    if not gate("B session b on the a-file: rc 0, saved == md5, peak {0} <= 690 and <= X10 {1} + 10".format(pk, x10),
                ok and (X.dry or sb.get("input") == AFILE), {"rc": rc, "final": bfile, "md5": bmd5}):
        return stop()
    X.write(L.STATE, {"a_file": AFILE, "a_md5": AMD5, "b_file": bfile, "b_md5": bmd5, "b_peak": pk, "resume": "launch_p3b2_resume_c135"})
    if not gate("B2 LabVIEW gone; bed + a-file unchanged", X.labview_gone() and L.md5(L.BED) == L.BED_MD5 and (X.dry or L.md5(AFILE) == AMD5)):
        return stop()
    arts.append({"path": bfile, "md5": bmd5})
    rc, seg = X.child("E")
    mv = re.search(r"ERRORLIST-VERDICT: (\w+) (.+)$", seg, re.M)
    if X.dry:
        R, cc = X.mem["e"], X.mem["e"]["cc"]
    else:
        R = L.J(mv.group(2).strip()) if mv and os.path.exists(mv.group(2).strip()) else {}
        import errorlist_check as EC
        cc = EC.class_counts(R.get("items"), ocr=True)
    rg, n = L.J(L.EL_RANGE), R.get("item_count")
    bad = dict((k, v) for k, v in cc.items() if not rg["per_class_lo"].get(k, 0) <= v <= rg["per_class_hi"].get(k, 0))
    bad.update(dict((k, 0) for k in rg["per_class_lo"] if k not in cc and rg["per_class_lo"][k] > 0))
    print("  FACT  E verdict {0}; items {1}; per class {2}".format(mv and mv.group(1), n, json.dumps(cc, sort_keys=True)), flush=True)
    gate("E full final Error List: reader gates all True, rc in (0, 1)", rc in (0, 1) and R.get("gates") and all(R["gates"].values()), R.get("gates"))
    gate("E2 total {0} in {1}..{2}".format(n, rg["total_lo"], rg["total_hi"]), n is not None and rg["total_lo"] <= n <= rg["total_hi"])
    gate("E3 every class within lo..hi of {0}".format(L.EL_RANGE), not bad, bad)
    gate("E4 LabVIEW gone; final, a-file and bed unchanged", X.labview_gone() and L.md5(L.BED) == L.BED_MD5
         and (X.dry or (L.md5(AFILE) == AMD5 and L.md5(bfile) == bmd5)))
    return stop()


if __name__ == "__main__":
    live = "--launch" in sys.argv[1:]
    br = sys.argv[sys.argv.index("--branch") + 1] if "--branch" in sys.argv else "equal"
    print("MODE {0}".format("LAUNCH" if live else "DRY (nothing spawned, nothing killed, nothing written), branch " + br), flush=True)
    X = L.Live() if live else L.Dry(br)
    gates, arts = run(X)
    if not live:
        print("  FACT  DRY calls {0}".format(X.calls), flush=True)
    np_, nf = sum(1 for _n, c in gates if c), sum(1 for _n, c in gates if not c)
    print(P.result_line(P.make_result(np_, nf, next((n for n, c in gates if not c), None), [a for a in arts if live and a.get("path")])), flush=True)
    sys.exit(1 if nf else 0)
