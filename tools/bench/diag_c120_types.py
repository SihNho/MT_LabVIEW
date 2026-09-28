r"""diag_c120_types - card 120-2 T2/T3 (PD237(k)) on a never-saved byte copy of the SAVED pool bed (D1_qrt_pool_20260928_141055.vi):
(H) the op-hygiene probe of the new reader OpTermDataType_v0 (built by build_op_termtype.py) - 1 warm + 2,000 consecutive calls on
DonorPool_v0 Traverse('Terminal')[0], 0 errors, same bytes every call, handles flat +-100 (the op-hygiene/1 criterion,
docs/violation-decisions.md 2026-09-28 10:37; the card's 20-call test is a subset) -> tools/bench/op_hygiene/; (T3) gscript.read_term_type
on the 9 terminals of diag_c120_types_plan.json -> tools/bench/facts_c120_types.json. Prior art: diag_c118_r1v.py (hygiene form, reused).
The work copy is never saved and is deleted; LabVIEW is killed at exit. No VI is run, nothing is edited.
PREDICTION: H 2000 calls, 0 errors, |dHandles| <= 100; R every read: uid echo == term, hex == u8 bytes, no error, rest '';
K K_DBL top TD Array with element DBL (0x0A), K_I32 Array with element I32 (0x03), F3 top TD I32 (0x03), K_DBL sig != K_I32 sig;
X bed and donor md5 unchanged.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c120_types.log -- py -u tools/bench/diag_c120_types.py"""
import contextlib, json, os, sys, time                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                               # noqa: E402
g = K.g
PL = json.load(open(os.path.join(ROOT, "tools/bench/diag_c120_types_plan.json"), encoding="utf-8"))   # one base resolves it (gate fp-5)
BED, BEDM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DON, DONM, NH = os.path.join(g.CLAUDEDEV, PL["hygiene"]["vi"]), PL["hygiene"]["md5"], PL["hygiene"]["calls"]
OPV, KEY = g.OP_TERM_DATA_TYPE, "OpTermDataType_v0"
OUTJ, OUTF = os.path.join(HERE, "diag_c120_types.json"), os.path.join(HERE, "facts_c120_types.json")
DRY = bool(getattr(g.report_all, "_dry", False))
N = 3 if DRY else NH
s = K.Stage(BED, BEDM, "scratch_c120_types", preload=False, deadline_min=28, reserve_s=150, out_json=OUTJ, task="card 120-2 T2/T3")
BP = K.mod("bench_prep")


def hyg():
    ctx = contextlib.nullcontext() if DRY else g.hygiene_probe(OPV)
    with ctx:
        i = PL["hygiene"]["index"]
        uid = int(g.report_all(DON, "Terminal")[i]["uid"]) if not DRY else 0
        first = g.read_term_type(DON, uid, index=i); h0, m0 = BP.labview_handles(), K.private_bytes()   # noqa: E702
        errs, codes, t0 = 0, [], time.time()
        for _k in range(N):
            r = g.read_term_type(DON, uid, index=i)
            if r["err"] or not r["hex_ok"] or r["bytes_hex"] != first["bytes_hex"]:
                errs += 1; codes.append((r["err"][:60], r["echo"])) if len(codes) < 5 else None   # noqa: E702
        h1, m1 = BP.labview_handles(), K.private_bytes()
    s.fact("HYG {0}: {1} calls in {2:.1f} s on DonorPool_v0 Terminal[{3}] #{4}, errors {5} {6}, handles {7} -> {8}, private {9} -> {10}, "
           "first {11}".format(KEY, N, time.time() - t0, i, uid, errs, codes, h0, h1, m0, m1, json.dumps(first, default=str)[:300]))
    ok = s.gate("H {0} {1} consecutive calls: 0 errors, same bytes, handles flat +-100".format(KEY, N),
                (errs == 0 and first["hex_ok"] and not first["err"] and abs(int(h1) - int(h0)) <= 100) if not DRY else True, (errs, h0, h1))
    if ok and not DRY:
        rec = {"schema": "op-hygiene/1", "op": KEY, "path": OPV, "md5": K.md5(OPV), "status": "PASS", "calls": N + 1, "errors": 0,
               "error_codes": [], "handles_before": h0, "handles_after": h1, "private_mb_before": round((m0 or 0) / 2 ** 20, 1),
               "private_mb_after": round((m1 or 0) / 2 ** 20, 1),
               "workload": "1 warm + {0} calls on Terminal #{1} (Traverse index {2}) of DonorPool_v0.vi (read-only)".format(N, uid, i),
               "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1): >= 2,000 consecutive calls, 0 errors, handles flat +-100",
               "log": "tools/bench/diag_c120_types.log", "build_log": "tools/bench/build_op_termtype.log",
               "script": "tools/bench/diag_c120_types.py", "card": "120-2", "date": time.strftime("%Y-%m-%d %H:%M")}
        json.dump(rec, open(os.path.join(HERE, "op_hygiene", KEY + ".json"), "w", encoding="utf-8"), indent=1)
        s.fact("HYGIENE RECORD op_hygiene/{0}.json".format(KEY))
    return ok


def body(_):
    s.start(); s.scratches.append(s.work); W = s.work                                 # noqa: E702
    s.gate("K0 donor DonorPool_v0 md5 == {0}".format(DONM), K.md5(DON) == DONM, K.md5(DON), fatal=True)
    s.head("[H] op-hygiene probe")
    s.gate("H hygiene record written (gscript.op admits OpTermDataType_v0)", hyg(), fatal=True)
    s.head("[R] read_term_type on the 9 terminals")
    order = [int(o["uid"]) for o in g.report_all(W, "Terminal")] if not DRY else []
    s.fact("Traverse('Terminal') on the work copy: {0} rows".format(len(order)))
    out = {"card": "120-2", "bed": PL["input"], "route": "gscript.read_term_type -> OpTermDataType_v0", "terms": {}}
    for t in PL["terms"]:
        idx = order.index(t["term"]) if t["term"] in order else None
        r, e = s.safe("read_term_type #{0}".format(t["term"]), lambda: g.read_term_type(W, t["term"], index=idx), {})
        r = r or {"err": e}
        ty = r.get("types") or {}
        s.fact("R {0} #{1}.{2!r} t{3}: canon {4} sig {5} err {6!r}".format(t["key"], t["node"], t["name"], t["term"], ty.get("canon"),
               (ty.get("sig") or "")[:80], r.get("err")))
        s.gate("R {0} t{1}: echo, hex == u8, no error, rest ''".format(t["key"], t["term"]), r.get("echo") == t["term"] and r.get("hex_ok")
               and not r.get("err") and r.get("rest") == "" and ty.get("sig"), (r.get("echo"), r.get("hex_ok"), r.get("err")))
        out["terms"][t["key"]] = dict(t, index=idx, echo=r.get("echo"), err=r.get("err"), bytes_hex=r.get("bytes_hex"), types=ty)
    T = out["terms"]
    cn = lambda k: (T[k].get("types") or {}).get("canon")                              # noqa: E731  label-free canon (gscript._td_canon)
    s.gate("K K_DBL canon == Array1D<DBL> (NAMES.md:37)", cn("K_DBL") == "Array1D<DBL>", cn("K_DBL"))
    s.gate("K K_I32 canon == Array1D<I32> (NAMES.md:41)", cn("K_I32") == "Array1D<I32>", cn("K_I32"))
    s.gate("K F3 loop i canon == I32", cn("F3") == "I32", cn("F3"))
    s.gate("K the reader distinguishes K_DBL from K_I32 (canon differs)", cn("K_DBL") != cn("K_I32"))
    out["known_checks"] = {"passes": list(s.passes), "fails": list(s.fails)}
    if not DRY:
        json.dump(out, open(OUTF, "w", encoding="utf-8"), indent=1)
        s.fact("FACTS written {0}".format(OUTF))
    s.gate("X donor md5 unchanged after the reads", K.md5(DON) == DONM, K.md5(DON))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
