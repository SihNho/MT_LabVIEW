r"""diag_c117a_joints - card 117-1 L3 (PD233(c)): Wire.Joints[] (gscript.wire_joints -> OpWireJoints_v1) of the 20 nets on a BYTE COPY
(claudeDev\scratch_c117_r2_<ts>.vi) of the SAVED L2-R2 file (path + md5 from tools/bench/stage_d1_l2r2.json l2r2), compared with card 116-4's
reads of the same recipe rows on a scratch (tools/bench/diag_c116d_j3_raw2.json: `before` = R1, `after` = 116-4's J4, decode.log:24-38).
PRIOR ART: diag_c116d_j3.py phase() (index from ONE report_all(Wire)), diag_c116d_decode.py dec() (flags & 0x100 LOOSE, & 0x1 terminal).
PREDICTION: every read echoes its uid, err ''; L3a the 13 outer nets: loose iff in J4's 9 (24277 24333 25237 25280 25306 25336 25911 26021
26064) or in {25438, 25461} (loose on R1 already), w25238/w25225 NOT loose, and (loose, joints, terminal joints) == 116-4 after, per net;
L3b the 7 PD230(d) nets carry the same joints as on R1 (raw == R1 read) for the 5 not on #637; 25438/25461 (also outer nets) == 116-4 after
(decode.log:32-33 shows them changed by the rows on the 116-4 scratch); copy deleted; saved file md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c117a_joints.log -- py -u tools/bench/diag_c117a_joints.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
J = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))                    # noqa: E731
ST, PRED, NETS, REF = J("stage_d1_l2r2.json")["l2r2"], J("plan_l2r2_pred.json"), J("diag_c116d_nets.json"), J("diag_c116d_j3_raw2.json")
O13, PD = [int(w) for w in PRED["shared_sink_nets"]], [int(w) for w in NETS["pd230"]]
J4 = {24277, 24333, 25237, 25280, 25306, 25336, 25911, 26021, 26064}; LOOSE_R1 = {25438, 25461}   # noqa: E702
SCR = os.path.join(g.CLAUDEDEV, "scratch_c117_r2_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
G, OUT = {}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:900]), flush=True); return bool(ok)  # noqa: E702


def dec(r):
    if not r or not r.get("joints"):
        return None
    j = r["joints"]
    return (sum(1 for x in j if int(x[1]) & 0x100), len(j), sum(1 for x in j if int(x[1]) & 0x1))


try:
    NEW = ST["final"]
    gate("K saved L2-R2 on disk, md5 == stage_d1_l2r2.json pin", bool(NEW) and os.path.exists(NEW) and md5(NEW) == ST["md5"], (NEW, ST["md5"]))
    shutil.copyfile(NEW, SCR)
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    order = [int(o["uid"]) for o in g.report_all(SCR, "Wire")]
    pos = dict((u, i) for i, u in enumerate(order))
    for w in sorted(set(O13) | set(PD)):
        OUT[w] = g.wire_joints(SCR, w, index=pos[w]) if w in pos else None
        r, a116, r1 = OUT[w], REF["after"].get(str(w)), REF["before"].get(str(w))
        print("  FACT  w%s echo %s err %r dec %s | 116-4 after %s | R1 %s | raw==116-4after %s | raw==R1 %s" % (
            w, r and r["echo"], r and r["err"], dec(r), dec(a116), dec(r1), bool(r and a116 and r["joints"] == a116["joints"]),
            bool(r and r1 and r["joints"] == r1["joints"])), flush=True)
    bad = [w for w, r in OUT.items() if not r or r["err"] or r["echo"] != w]
    gate("R every one of the %d nets present and read (echo == uid, err '')" % len(OUT), not bad, bad)
    lo = set(w for w in O13 if dec(OUT.get(w)) and dec(OUT[w])[0])
    gate("L3a loose outer nets == J4's 9 + {25438, 25461}; w25238/w25225 not loose", lo == J4 | LOOSE_R1 and not lo & {25238, 25225},
         {"loose": sorted(lo), "extra": sorted(lo - J4 - LOOSE_R1), "missing": sorted((J4 | LOOSE_R1) - lo)})
    mm = [(w, dec(OUT.get(w)), dec(REF["after"].get(str(w)))) for w in O13 if dec(OUT.get(w)) != dec(REF["after"].get(str(w)))]
    gate("L3a (loose, joints, terminal joints) == 116-4's after-read for all 13 outer nets", not mm, mm)
    pb = [(w, dec(OUT.get(w)), dec(REF["before"].get(str(w)))) for w in PD if w not in O13 and not (OUT.get(w) and REF["before"].get(str(w))
          and OUT[w]["joints"] == REF["before"][str(w)]["joints"])]
    pb += [(w, dec(OUT.get(w)), dec(REF["after"].get(str(w)))) for w in PD if w in O13 and dec(OUT.get(w)) != dec(REF["after"].get(str(w)))]
    gate("L3b PD230(d) nets: the 5 off #637 raw joints == R1; 25438/25461 == 116-4 after", not pb, pb)
    json.dump(dict((str(k), v) for k, v in OUT.items()), open(os.path.join(HERE, "diag_c117a_joints_raw.json"), "w", encoding="utf-8"), default=str)
except Exception as e:                                                                       # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for _i in range(5):
        try:
            os.path.exists(SCR) and os.remove(SCR); break                                    # noqa: E702
        except OSError:
            time.sleep(3)
    NEW = ST.get("final")
    gate("H LabVIEW gone; copy deleted; saved file md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
         and not os.path.exists(SCR) and bool(NEW) and os.path.exists(NEW) and md5(NEW) == ST.get("md5"))
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    sys.exit(1 if bad else 0)
