r"""diag_c118_r1v - card 118-4 R1/R2/A2 on a never-saved byte copy of the SAVED R2 (D1_l2_r2_20260928_110756.vi): (H) the op-hygiene
probe of the two new readers built by diag_c118_r1_opbuild.py (OpConstValueRing_v0, OpConstValueArr_v0; 1 warm + 2,000 consecutive calls
each, 0 errors, handles flat +-100 - the op-hygiene/1 criterion, docs/violation-decisions.md 2026-09-28 10:37) -> tools/bench/op_hygiene/;
(R1) gscript.read_const_value on #23583 (StringConstant, known 'Cam', diag_c118_p0.json:445) and #13245 (RingConstant, value + type);
(R2) the same verb on claudeDev\OpPoolDonor_v0.vi #101 (ArrayConstant; READ-ONLY, the donor is never run or saved) == Cam_pool00..19;
(A2) gscript.create_primitive_nested(W, 13236, donor #101) - the ArrayConstant exception (PD234(j)(2)) - then the copy read back with the
R1 reader == Cam_pool00..19. The work copy is never saved and is deleted; LabVIEW is killed at exit. No VI is run.
PREDICTION: H1/H2 2,000 calls, 0 errors, |dHandles| <= 100 per op; R1a 'Cam' echo 23583; R1b ring value an int, Representation read,
echo 13245, no error; R2 == NAMES, echo 101; A2a one ArrayConstant uid returned, owner Diagram #13236 (checked inside the verb);
A2b its value == NAMES; K R2 md5 unchanged (Stage H2).
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c118_r1v.log -- py -u tools/bench/diag_c118_r1v.py"""
import contextlib, json, os, sys, time                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                               # noqa: E402
g = K.g
PLP = os.path.join(HERE, "diag_c118_r1v_plan.json"); PL = json.load(open(PLP, encoding="utf-8"))   # noqa: E702  ONE literal: stage_prerun.plan_files
Q, DN = PL["p0"], PL["donor"]
R2, R2M, FRAME, POS = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], Q["frame"], tuple(PL["pos"]["names"])
DONOR, DONOR_MD5, NAMES_UID = os.path.join(g.CLAUDEDEV, DN["vi"]), DN["md5"], DN["names"]
NAMES = ["{0}_pool{1:02d}".format(Q["base_name"], k) for k in range(20)]           # PD234(h)
LABS = json.load(open(os.path.join(HERE, "diag_c118_oplabels.json"), encoding="utf-8"))
OUTJ, HYG, SV = os.path.join(HERE, "diag_c118_r1v.json"), os.path.join(HERE, "op_hygiene"), os.path.join(HERE, "scratch_verify")
DRY = bool(getattr(g.report_all, "_dry", False))
N, LN = (3 if DRY else PL["hygiene_calls"]), 6 * 99
s = K.Stage(R2, R2M, "scratch_c118_r1v", preload=False, deadline_min=33, reserve_s=150, out_json=OUTJ, task="card 118-4")
BP = K.mod("bench_prep")


def hyg(key, tgt, cls, uid):
    lab, path = LABS[key], os.path.join(g.CLAUDEDEV, key + ".vi")
    ctx = contextlib.nullcontext() if DRY else g.hygiene_probe(path)
    with ctx:
        i = [int(o["uid"]) for o in g.report_all(tgt, cls)].index(uid) if not DRY else 0
        vi = g.op(path); g._set_common(vi, tgt, lab, cls, i); g._run(vi)            # noqa: E702  warm call
        first = vi.GetControlValue(lab["Value"]); h0, m0 = BP.labview_handles(), K.private_bytes()   # noqa: E702
        errs, codes, t0 = 0, [], time.time()
        for _k in range(N):
            vi.SetControlValue(lab["UID"], 0); g._run(vi)                             # noqa: E702
            e, echo, v = str(g._err(vi, lab["Err"]) or ""), vi.GetControlValue(lab["UID"]), vi.GetControlValue(lab["Value"])
            if e or echo != uid or v != first:
                errs += 1; codes.append((e[:60], echo)) if len(codes) < 5 else None   # noqa: E702
        h1, m1 = BP.labview_handles(), K.private_bytes()
    s.fact("HYG {0}: {1} calls in {2:.1f} s, errors {3} {4}, handles {5} -> {6}, private {7} -> {8}, value {9!r:.120}".format(key, N, time.time() - t0, errs, codes, h0, h1, m0, m1, first))
    ok = s.gate("H {0} {1} consecutive calls on #{2}: 0 errors, handles flat +-100".format(key, N, uid), errs == 0 and abs(int(h1) - int(h0)) <= 100 if not DRY else h1, (errs, h0, h1))
    if ok and not DRY:
        rec = {"schema": "op-hygiene/1", "op": key, "path": path, "md5": K.md5(path), "status": "PASS", "calls": N + 1, "errors": 0, "error_codes": [],
               "handles_before": h0, "handles_after": h1, "private_mb_before": round((m0 or 0) / 2 ** 20, 1), "private_mb_after": round((m1 or 0) / 2 ** 20, 1),
               "workload": "1 warm + {0} calls on {1} #{2} of {3} (read-only)".format(N, cls, uid, os.path.basename(tgt)),
               "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1): >= 2,000 consecutive calls, 0 errors, handles flat +-100",
               "log": "tools/bench/diag_c118_r1v.log", "build_log": "tools/bench/diag_c118_r1_opbuild.log", "script": "tools/bench/diag_c118_r1v.py",
               "card": "118-4", "date": time.strftime("%Y-%m-%d %H:%M")}
        json.dump(rec, open(os.path.join(HYG, key + ".json"), "w", encoding="utf-8"), indent=1); s.fact("HYGIENE RECORD op_hygiene/{0}.json".format(key))   # noqa: E702
    return ok


def body(_):
    s.start(); s.scratches.append(s.work); W = s.work                                 # noqa: E702
    s.gate("K0 donor OpPoolDonor_v0 md5 == {0}".format(DONOR_MD5), K.md5(DONOR) == DONOR_MD5, K.md5(DONOR), fatal=True)
    s.head("[H] op-hygiene probes")
    okh = [hyg("OpConstValueRing_v0", W, "RingConstant", Q["ring"]), hyg("OpConstValueArr_v0", DONOR, "ArrayConstant", NAMES_UID)]
    s.gate("H both hygiene records written (gscript.op admits the ops)", all(okh), okh, fatal=True)
    s.head("[R] read_const_value")
    rs, _e1 = s.safe("read name constant", lambda: g.read_const_value(W, Q["name_const"]), {})
    s.fact("R1a #{0} {1}".format(Q["name_const"], json.dumps(rs, default=str)[:LN]))
    s.gate("R1a #{0} StringConstant == {1!r}, uid echo, no error".format(Q["name_const"], Q["name_value"]), rs and rs.get("value") == Q["name_value"] and rs.get("echo") == Q["name_const"] and not rs.get("err"), rs and rs.get("err"))
    rr, _e2 = s.safe("read ring", lambda: g.read_const_value(W, Q["ring"]), {})
    s.fact("R1b #{0} {1}".format(Q["ring"], json.dumps(rr, default=str)[:LN]))
    s.gate("R1b #{0} RingConstant: int value + Representation read, uid echo, no error".format(Q["ring"]), rr and rr.get("cls") == "RingConstant" and isinstance(rr.get("value"), int)
           and "representation" in (rr.get("type") or {}) and rr.get("echo") == Q["ring"] and not rr.get("err"), rr and (rr.get("value"), rr.get("type"), rr.get("err")))
    ra, _e3 = s.safe("read donor names", lambda: g.read_const_value(DONOR, NAMES_UID), {})
    s.fact("R2 donor #{0} {1}".format(NAMES_UID, json.dumps(ra, default=str)[:LN]))
    s.gate("R2 donor #{0} ArrayConstant value == Cam_pool00..19, uid echo, no error".format(NAMES_UID), ra and list(ra.get("value") or []) == NAMES and ra.get("echo") == NAMES_UID and not ra.get("err"), ra and (ra.get("type"), ra.get("err")))
    s.head("[A2] ArrayConstant copy onto frame diagram #{0}".format(FRAME))
    arr, e4 = s.safe("create_primitive_nested", lambda: g.create_primitive_nested(W, FRAME, "pool_names", POS, donor={"donor": DONOR, "uid": NAMES_UID}), None)
    s.gate("A2a create_primitive_nested returned ONE ArrayConstant uid owned by Diagram #{0} (no refusal)".format(FRAME), arr and not e4, (arr, e4))
    rc, _e5 = s.safe("read copy", lambda: g.read_const_value(W, arr), {}) if arr else ({}, "no copy")
    s.fact("A2b copy #{0} {1}".format(arr, json.dumps(rc, default=str)[:LN]))
    s.gate("A2b the copy reads back == Cam_pool00..19 with the R1 reader", rc and list(rc.get("value") or []) == NAMES and not rc.get("err"), rc and (rc.get("type"), rc.get("err")))
    s.gate("K donor md5 unchanged after the reads and the copy", K.md5(DONOR) == DONOR_MD5, K.md5(DONOR))
    if not s.fails and not DRY:
        for fn in ("gscript.create_primitive_nested", "gscript.read_const_value"):
            p = os.path.join(SV, "{0}_c118_{1}.json".format(fn, s.stamp))
            json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "118-4 A2", "log": "tools/bench/diag_c118_r1v.log", "input_md5": R2M,
                       "fixture": "never-saved byte copy of claudeDev\\D1_l2_r2_20260928_110756.vi (deleted) + OpPoolDonor_v0 #101 read-only",
                       "ops": dict((k, v["md5"]) for k, v in LABS.items())}, open(p, "w", encoding="utf-8"), indent=1)
            s.fact("SCRATCH-VERIFY record {0}".format(p))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
