r"""diag_c122_hyg - card 122-4 (PD242(a)(b)): the constant DONOR + the op-hygiene record of claudeDev\OpConstInd_v0.vi.
PRIOR ART (checked, reused): donor() is diag_c122_route.py's (card 122-3, never run) = the proven donor form of diag_c118_p1.py:29-46
(create_const_loop_term(value=) on PARALLEL_kernel_v3.vi's typed sinks, NAMES.md:37/41; a For loop's N for the I32 scalar);
the hygiene record schema + 2,000-call criterion = diag_c118_r1v.py / op_hygiene/OpConstValueArr_v0.json (docs/violation-decisions.md
2026-09-28 10:37 (1)); gscript.hygiene_probe is the one exemption while measuring. No new op.
(D) claudeDev\DonorRingConst_v0.vi from EMPTY_v0: DBL[20] 0.0, I32[20] -1, I32 -1; kernel subVI deleted (checked by CLASS at its uid,
PD242(a)); values read back; ES 1; saved. Kernel md5 unchanged. (H) a CREATOR: each call adds one indicator, so the probe RECYCLES -
round k = a fresh never-saved byte copy of the donor, CALLS op calls, close+delete; handles read with NO scratch loaded (equal VI state,
PD242(b)) after the warm round and after every round. Round 0 = warm: one full create_indicator_on_const (effect checks) + 4 raw calls.
PREDICTION: D0 kernel #uk not a SubVI after delete; D1 3 constants; D2 values == written; D3 ES 1; K kernel md5 unchanged;
H1 the warm call: echo == const uid, one new wired indicator; H2 ROUNDS x CALLS = 2000 raw calls, 0 errors, every echo == const uid,
every round +CALLS ControlTerminals; H3 |handles(after last round) - handles(after warm)| <= 100 -> op_hygiene/OpConstInd_v0.json.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c122_hyg.log -- py -u tools/bench/diag_c122_hyg.py"""
import json, os, shutil, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                 # noqa: E402
g = K.g
EMPTY, KERN, DON = (os.path.join(g.CLAUDEDEV, n) for n in ("EMPTY_v0.vi", "PARALLEL_kernel_v3.vi", "DonorRingConst_v0.vi"))
PL = json.load(open(os.path.join(HERE, "diag_c122_hyg_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
N20, ROUNDS, CALLS, OUTJ = 20, PL["rounds"], PL["calls"], os.path.join(HERE, "diag_c122_hyg.json")
DRY = bool(getattr(g.report_all, "_dry", False))                                     # input = the saved R2 (a scratch work copy, as diag_c118_r1v.py)
s = K.Stage(os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], "scratch_c122_hyg", preload=False, deadline_min=42, reserve_s=150,
            out_json=OUTJ, task="card 122-4")
B, BP = K.mod("build_track_v6_core"), K.mod("bench_prep")
same = lambda a, b: tuple(a) == tuple(b) if isinstance(b, list) else a == b          # noqa: E731


def donor():
    km = K.md5(KERN)
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(EMPTY, DON); g.open_panel(DON)   # noqa: E702
    uk = B.drop(DON, KERN, 0, (300, 200)); wk = B.walk(DON, 0)                      # noqa: E702
    rx = g.create_const_loop_term(DON, "for_n", wk[uk][0], value=[0.0] * N20, term_index=B.term(wk[uk][2], "x,y,z array", False)["i"])
    rp = g.create_const_loop_term(DON, "for_n", wk[uk][0], value=[-1] * N20, term_index=B.term(wk[uk][2], "pos in cal image in", False)["i"])
    f0 = g.uids(DON, "ForLoop"); g.for_loop(DON, (300, 500)); uf = sorted(g.uids(DON, "ForLoop") - f0)[0]   # noqa: E702
    rn = g.create_const_loop_term(DON, "for_n", B.walk(DON, 0)[uf][0], value=-1)
    s.fact("DONOR consts dbl {0} i32[] {1} i32 {2}".format(rx, rp, rn))
    rec = {"dbl_20": rx["created_uid"], "i32_20": rp["created_uid"], "i32": rn["created_uid"]}
    s.gate("D1 three constants created, no invoke error", all(rec.values()) and not any(r["inv_err"] for r in (rx, rp, rn)), rec, fatal=True)
    g.delete_object(DON, "SubVI", B.sub_i(DON, uk), verify=False); g.remove_bad_wires_scripted(DON)   # noqa: E702
    s.gate("D0 kernel deleted: #{0} is no longer a SubVI (class at uid, PD242(a))".format(uk), int(uk) not in set(int(u) for u in g.uids(DON, "SubVI")), uk, fatal=True)
    want = {"i32": -1, "i32_20": [-1] * N20, "dbl_20": [0.0] * N20}
    got = dict((k, g.read_const_value(DON, u)) for k, u in rec.items())
    s.fact("DONOR READ {0}".format(json.dumps(got, default=str)[:900]))
    s.gate("D2 donor values read back == written", all(same(got[k]["value"], want[k]) and not got[k]["err"] for k in rec), fatal=True)
    s.gate("D3 donor ES 1 -> saved", g.exec_state(DON) == 1, fatal=True)
    g.save(DON); g.close_panel(DON); rec["md5"] = K.md5(DON); rec["classes"] = dict((k, v["cls"]) for k, v in got.items())   # noqa: E702
    s.fact("DONOR RECORD {0}".format(rec))
    s.gate("K kernel PARALLEL_kernel_v3.vi md5 unchanged (dropped, never saved)", K.md5(KERN) == km, km)
    json.dump(dict(rec, path=DON, card="122-4", log="tools/bench/diag_c122_hyg.log"), open(os.path.join(HERE, "diag_c122_donor.json"), "w"), indent=1)
    return rec


def raw(vi, lab, sc, cls, i, cu):
    g._set_common(vi, sc, lab, cls, i); vi.SetControlValue(lab["UID"], 0); g._run(vi)   # noqa: E702
    e = str(g._err(vi, lab["Err"]) or ""); echo = int(vi.GetControlValue(lab["UID"]))   # noqa: E702
    return e + ("" if echo == int(cu) else " echo %r != #%s" % (echo, cu))


def hyg(rec):
    lab = json.load(open(g.C122_LABELS, encoding="utf-8"))["OpConstInd_v0"]
    cu, errs, hs, ms, dct, t0 = rec["i32"], [], [], [], [], time.time()
    with g.hygiene_probe(g.OP_CONST_IND):
        vi = g.op(g.OP_CONST_IND)
        for k in range(ROUNDS + 1):
            sc = s.scratch("h%02d" % k, DON); cls, i = g.const_class_index(sc, cu); c0 = len(g.uids(sc, "ControlTerminal"))   # noqa: E702
            if k == 0:
                r0 = g.create_indicator_on_const(sc, cu)
                s.gate("H1 warm call: echo == #{0}, ONE new wired indicator".format(cu), not r0["err"] and r0["echo"] == cu and r0["created_uid"], r0, fatal=True)
            n = 4 if k == 0 else CALLS
            e = [x for x in (raw(vi, lab, sc, cls, i, cu) for _j in range(n)) if x]
            dct.append(len(g.uids(sc, "ControlTerminal")) - c0)
            k and errs.extend(e)                                                     # noqa: E701
            s.drop_scratch(sc, "H-r%02d" % k); hs.append(BP.labview_handles()); ms.append(K.private_bytes())   # noqa: E702
            s.fact("HYG round {0}: {1} calls, errors {2} {3}, +ControlTerminal {4}, handles {5}, private {6}, t {7:.0f}s".format(
                k, n, len(e), e[:2], dct[-1], hs[-1], ms[-1], time.time() - t0))
    ok2 = s.gate("H2 {0} x {1} = {2} raw calls, 0 errors (echo == #{3}), each round +{1} ControlTerminals".format(ROUNDS, CALLS, ROUNDS * CALLS, cu),
                 not errs and dct[1:] == [CALLS] * ROUNDS, {"errors": errs[:5], "dct": dct})
    ok3 = s.gate("H3 handles at equal VI state (no scratch loaded): |last - warm| <= 100", abs(hs[-1] - hs[0]) <= 100,
                 {"warm": hs[0], "last": hs[-1], "max_dev": max(abs(h - hs[0]) for h in hs)})
    if ok2 and ok3:
        json.dump({"schema": "op-hygiene/1", "op": "OpConstInd_v0", "path": g.OP_CONST_IND, "md5": K.md5(g.OP_CONST_IND), "status": "PASS",
                   "calls": ROUNDS * CALLS + 5, "errors": 0, "error_codes": [], "handles_before": hs[0], "handles_after": hs[-1],
                   "handles_per_round": hs, "private_mb_before": ms[0], "private_mb_after": ms[-1],
                   "workload": "warm round (1 create_indicator_on_const + 4 raw) then {0} rounds x {1} consecutive raw OpConstInd_v0 calls on I32 "
                               "constant #{2} of a fresh never-saved byte copy of DonorRingConst_v0.vi (recycled per round, PD242(b))".format(ROUNDS, CALLS, cu),
                   "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1) + PD242(b): >= 2,000 consecutive calls, 0 errors, handles flat +-100 at equal VI state",
                   "log": "tools/bench/diag_c122_hyg.log", "build_log": "tools/bench/diag_c122_opbuild.log", "script": "tools/bench/diag_c122_hyg.py",
                   "card": "122-4", "date": time.strftime("%Y-%m-%d %H:%M")},
                  open(os.path.join(HERE, "op_hygiene", "OpConstInd_v0.json"), "w", encoding="utf-8"), indent=1)
        s.fact("WROTE op_hygiene/OpConstInd_v0.json")


def body(_):
    s.start(); s.discard_work()                                                      # noqa: E702
    DRY or hyg(donor())                                                              # dry: COM is stubbed, nothing to measure
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
