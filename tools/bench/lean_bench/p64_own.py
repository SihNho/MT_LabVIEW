# ---
# labview: none
# hardware: none
# ---
r"""p64_own - offline, read-only (P6-4 preparation P-3): acceptance #1's LIVE half on the OBS leg, plan section 6.3, with the LOGGED
start value (never a fitted constant).
Inputs: the wrapper file (GetBuffFirst, one line `S<TAB>R<TAB>tick`: S = requested `Buffer to extract` on the first call = the
LastBufferNumber #5119 subtracts, R = returned `current image number`; `lean_report_p64p1.md:188-189`), the pick log (BOBS90's pick
observer, one line per pick: Num[0..19], last, picked, slot, tick; `latest_picklag.py:2`) and the leg's run dir (tra column 0).
  NOT RUN  the wrapper file is missing or does not hold exactly 1 line (plan :195-196) - never PASS, never a fitted C.
  step 1   R - S recorded (expected 0: the camera gave the requested buffer; Missed frames? = (S == R)).
  step 2   row k is paired with pick k (the FIRST `rows` picks, same index, no skipping, no re-matching): PASS only if rows > 0,
           pick-log lines >= rows and col0[k] + S - picked[k] == 0 on every row (histogram exactly {0: rows}). Picks after the
           last row (index >= rows) are counted and listed (first 5), no upper limit, not judged. A first or middle pick with no
           row breaks the pairing -> FAIL "OWN 대응 근거 부족" (insufficient evidence that each row is its own pick's - NOT called
           a product computation error) with the first failing k, its col0, S, picked. latest_picklag.join (in-order
           subsequence) is kept only as the recorded field join_reference; it does not feed the verdict (review p64p3 c2 :11-16).
  step 3   col0[0] >= R - S (no row older than the first frame).
  step 4   lag at the pick (ring max - picked) in 0..19 on every pick (inside the ring); the 0-share is recorded.
  recorded end lag = frame counter at stop (leg json `frame=`) - (S + last col0).
U32 decode as stated in `lean_report_latest.md:47-49` (latest_picklag.dec) for both files.
    py tools/bench/lean_bench/p64_own.py --getbuff <file> --picklog <file> --run <run dir> [--leg-json <leg.json>] [--out <json>]
    py tools/bench/lean_bench/p64_own.py --dry     -> the recorded W100OBS leg + TEMP stand-ins (1.3 of lean_report_p64p3.md)"""
import json, os, shutil, struct, sys, tempfile, time                                      # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import latest_picklag as LP, protocol as P, p6close_sum as PS                            # noqa: E401,E402
RING = 20


def read_getbuff(path):
    """The wrapper file -> (lines, error). lines = [[S, R, tick]] decoded; a missing file -> ([], 'missing')."""
    if not os.path.isfile(path):
        return [], "missing"
    L = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        if ln.strip():
            v = [int(round(float(x))) for x in ln.replace(",", "\t").split()]
            L.append([LP.dec(x) for x in v[:2]] + v[2:])
    return L, None


def check(gb_lines, picks, col0, frame_at_stop=None):
    """Plan 6.3 on decoded inputs. gb_lines from read_getbuff, picks = latest_picklag.parse lines, col0 = ints.
    Returns {verdict: PASS|FAIL|NOT RUN, why, steps...}."""
    out = {"wrapper_lines": len(gb_lines)}
    if len(gb_lines) != 1:
        out.update({"verdict": "NOT RUN", "why": "wrapper file holds %d lines, not exactly 1 (plan 6.3; no fitted constant)" % len(gb_lines)})
        return out
    S, R = gb_lines[0][0], gb_lines[0][1]
    rows = LP.picklag(picks)
    pk = [r["picked"] for r in rows]
    c = [int(x) for x in col0]
    out["S"], out["R"], out["R_minus_S"] = S, R, R - S
    n = min(len(c), len(pk))
    d = [c[k] + S - pk[k] for k in range(n)]                  # row k against pick k: the pick that produced it (plan 6.3 step 2)
    bad = [k for k in range(n) if d[k] != 0]
    first = bad[0] if bad else (n if len(pk) < len(c) else None)          # a row with no pick fails at k = log lines
    s2 = bool(c) and len(pk) >= len(c) and first is None
    trail = pk[len(c):]
    out["step2"] = {"pass": s2, "rows": len(c), "log_lines": len(pk), "pairing_1to1_col0_plus_S_minus_picked_hist": LP.hist(d),
                    "first_failing": None if first is None else {"k": first, "col0": c[first] if first < len(c) else None, "S": S,
                                                                 "picked": pk[first] if first < len(pk) else None},
                    "trailing_picks": len(trail), "trailing_picked_first5": trail[:5],
                    "join_reference": {k: v for k, v in LP.join(rows, [x + S for x in c]).items() if k != "picks_without_row"}}
    if not c:
        out["step2"]["why"] = "no saved rows"
    elif not s2:
        out["step2"]["why"] = "OWN 대응 근거 부족 (row k vs pick k): %s%s" % (
            "pick-log lines %d < rows %d; " % (len(pk), len(c)) if len(pk) < len(c) else "",
            "first failing k %d, col0 %s, S %d, picked %s" % (first, out["step2"]["first_failing"]["col0"], S, out["step2"]["first_failing"]["picked"]))
    s3 = bool(c) and c[0] >= R - S
    out["step3"] = {"pass": s3, "col0_first": c[0] if c else None, "R_minus_S": R - S}
    lp = [r["lag_pick"] for r in rows]
    s4 = bool(lp) and all(0 <= x <= RING - 1 for x in lp)
    out["step4"] = {"pass": s4, "lag_pick_hist": LP.hist(lp), "share_lag0": round(sum(1 for x in lp if x == 0) / float(len(lp)), 4) if lp else None}
    out["end_lag"] = (frame_at_stop - (S + c[-1])) if (frame_at_stop is not None and c) else None
    out["frame_at_stop"] = frame_at_stop
    out["verdict"] = "PASS" if (s2 and s3 and s4) else "FAIL"
    out["why"] = None if out["verdict"] == "PASS" else "failed: %s%s" % ([k for k, v in (("step2", s2), ("step3", s3), ("step4", s4)) if not v],
                                                                          "; step2: %s" % out["step2"]["why"] if not s2 else "")
    return out


# self-check: a 3-row toy (S = 100) - exact rows PASS, a +1 row offset FAIL, 2 wrapper lines NOT RUN
_tp = [[101, 102] + [-1] * 18 + [100, 102, 1, 5], [101, 102, 103, 104] + [-1] * 16 + [102, 104, 3, 9], [105, 102, 103, 104] + [-1] * 16 + [104, 105, 0, 12]]
assert check([[100, 101, 1]], _tp, [2, 4, 5])["verdict"] == "PASS"
assert check([[100, 101, 1]], _tp, [3, 5, 6])["verdict"] == "FAIL"
assert check([[100, 101, 1], [100, 101, 2]], _tp, [2, 4, 5])["verdict"] == "NOT RUN"
# the review's counterexample (round_01_gpt.md:7): S = R = 100, consecutive picks 100..103 (lag 0) - the in-order subsequence
# join PASSed rows [1, 2, 3] by skipping pick 100; row k vs pick k does not
_tc = [[p] + [-1] * 19 + [p - 1, p, 0, p] for p in (100, 101, 102, 103)]
assert check([[100, 100, 1]], _tc, [0, 1, 2])["verdict"] == "PASS"
assert check([[100, 100, 1]], _tc, [1, 2, 3])["verdict"] == "FAIL"
assert check([[100, 100, 1]], _tc[:1], [0, 1])["verdict"] == "FAIL"


def run(getbuff, picklog, run_dir, leg_json=None):
    import m8b_replay_compare as M
    gb, err = read_getbuff(getbuff)
    picks, bad = LP.parse(picklog) if os.path.isfile(picklog) else ([], ["pick log missing"])
    info, t = M.tra(run_dir)
    fas = PS.leg_facts(leg_json).get("frame_at_stop") if leg_json else None
    r = check(gb, picks, [] if t is None else t[:, 0], fas)
    r.update({"getbuff": getbuff, "getbuff_error": err, "picklog": picklog, "picklog_bad_lines": bad, "run_dir": run_dir, "tra": info})
    if err:
        r["why"] = "wrapper file %s (plan 6.3; no fitted constant)" % err
    return r


def tra_copy(src_dir, dst_dir, fn=None, drop=()):
    """TEMP mock only: copy a run dir's tra file with column 0 replaced by fn(col0 array) and the rows `drop` removed (the row
    count in the header follows; same header and layout)."""
    import m8b_replay_compare as M
    info, t = M.tra(src_dir)
    b = bytearray(open(info["file"], "rb").read())
    k = b.find(b"not in z!)") + 10
    r, c = struct.unpack("<ii", bytes(b[k:k + 8]))
    a = np.frombuffer(bytes(b[k + 8:k + 8 + 8 * r * c]), dtype="<f8").reshape(r, c).copy()
    if fn is not None:
        a[:, 0] = fn(a[:, 0].copy())
    a = np.delete(a, list(drop), axis=0)
    os.makedirs(dst_dir, exist_ok=True)
    open(os.path.join(dst_dir, os.path.basename(info["file"])), "wb").write(
        bytes(b[:k]) + struct.pack("<ii", len(a), c) + a.astype("<f8").tobytes() + bytes(b[k + 8 + 8 * r * c:]))
    return dst_dir


def M_tra_col0(run_dir):
    import m8b_replay_compare as M
    return [int(x) for x in M.tra(run_dir)[1][:, 0]]


def synth_picklog(path, S, n, ring=RING):
    """TEMP mock only: n pick-log lines in the exact format of out_latest2/picklog_w100.txt (latest_picklag.parse): Num[0..19]
    (a ring written in order from S; never-written slots -1 written as U32 4294967295), last, picked = S + k, slot, tick.
    The picked Num is the ring max, so the lag at the pick is 0 on every line."""
    with open(path, "w") as f:
        for k in range(n):
            p = S + k
            num = [-1] * ring
            for q in range(max(S, p - ring + 1), p + 1):
                num[(q - S) % ring] = q
            v = num + [p - 1, p, (p - S) % ring, 142998000 + 59 * k]
            f.write("\t".join(str(x + 2 ** 32 if x < 0 else x) for x in v) + "\n")
    return path


OBS_RUN = os.path.join(HERE, "out_latest2", "run", "replay_s1_20261014_033411")
OBS_LOG = os.path.join(HERE, "out_latest2", "picklog_w100.txt")
OBS_LEG = os.path.join(HERE, "out_latest2", "legs", "W100OBS_a1", "leg.json")
FUNCTEST = os.path.join(HERE, "out_p64", "getbuff_first_functest_20261014_114246.txt")
CONSEC_RUN = os.path.join(HERE, "out_p6close", "run", "replay_s1_20261014_040041")     # P62: 2540 rows, col0 0..2539, 0 lost


def dry():
    tmp = tempfile.mkdtemp(prefix="p64own_mock_")
    G, res = {}, {}
    H = "pairing_1to1_col0_plus_S_minus_picked_hist"

    def one_case(tag, gbf, log, rd, leg, want):
        r = run(gbf, log, rd, leg)
        res[tag] = {k: r.get(k) for k in ("verdict", "why", "wrapper_lines", "R_minus_S", "end_lag", "frame_at_stop")}
        for s in ("step2", "step3", "step4"):
            if s in r:
                res[tag][s] = r[s]
        print("CASE %-44s %s" % (tag, json.dumps(res[tag], default=str, ensure_ascii=False)), flush=True)
        G["O %s -> %s" % (tag, want)] = r["verdict"] == want
        return res[tag]

    def s2(tag):
        return res[tag]["step2"]

    def ff(tag):
        f = s2(tag)["first_failing"]
        return None if f is None else (f["k"], f["col0"], f["S"], f["picked"])
    try:
        one = os.path.join(tmp, "getbuff_one.txt"); open(one, "w").write("20896\t20896\t142998000\n")
        zero = os.path.join(tmp, "getbuff_zero.txt"); open(zero, "w").write("")
        two = os.path.join(tmp, "getbuff_two.txt"); open(two, "w").write("20896\t20896\t142998000\n20896\t20896\t142999000\n")
        # --- the 7 kept cases (W100OBS rows + its recorded pick log; W100 has 1068 lost frames)
        shifted = tra_copy(OBS_RUN, os.path.join(tmp, "run_shift1"), lambda c: c + 1)
        lap = tra_copy(OBS_RUN, os.path.join(tmp, "run_lap20"), lambda c: np.concatenate([c[:20], c[20:] - 20]))
        cases = {"recorded": (one, OBS_RUN, "PASS"), "shifted +1": (one, shifted, "FAIL"), "one-lap-old": (one, lap, "FAIL"),
                 "wrapper 0 lines": (zero, OBS_RUN, "NOT RUN"), "wrapper 2 lines": (two, OBS_RUN, "NOT RUN"),
                 "wrapper 4 lines (functest file)": (FUNCTEST, OBS_RUN, "NOT RUN"), "wrapper missing": (os.path.join(tmp, "none.txt"), OBS_RUN, "NOT RUN")}
        for tag, (gbf, rd, want) in cases.items():
            one_case(tag, gbf, OBS_LOG, rd, OBS_LEG, want)
        c_obs = M_tra_col0(OBS_RUN)
        rr = res["recorded"]
        G["O recorded: R-S 0, {0: 1474}, 1 trailing pick (23439), col0[0] 0, lag 0 on 1475, end lag 2, W100 lost 1068"] = (
            rr["R_minus_S"] == 0 and s2("recorded")["rows"] == 1474 and s2("recorded")[H] == {0: 1474} and s2("recorded")["trailing_picks"] == 1
            and s2("recorded")["trailing_picked_first5"] == [23439] and rr["step3"]["col0_first"] == 0 and rr["step4"]["lag_pick_hist"] == {0: 1475}
            and rr["end_lag"] == 2 and (c_obs[-1] - c_obs[0] + 1) - len(c_obs) == 1068)
        G["O shifted: {1: 1474}, first failing k 0 (col0 1, S 20896, picked 20896)"] = s2("shifted +1")[H] == {1: 1474} and ff("shifted +1") == (0, 1, 20896, 20896)
        G["O one-lap-old: {0: 20, -20: 1454}, first failing k 20"] = (s2("one-lap-old")[H] == {-20: 1454, 0: 20} and ff("one-lap-old")[0] == 20
                                                                     and ff("one-lap-old")[1] == c_obs[20] - 20 and ff("one-lap-old")[3] == c_obs[20] + 20896)
        # --- the 6 new cases on a CONSECUTIVE leg (no lost frames - what W100 cannot show): P62 rows + a TEMP synthetic pick log
        c_p62 = M_tra_col0(CONSEC_RUN)
        G["O consecutive leg: P62 2540 rows, col0 0..2539, 0 lost"] = len(c_p62) == 2540 and list(c_p62) == list(range(2540))
        nr = len(c_p62)
        log1 = synth_picklog(os.path.join(tmp, "picklog_consec_1trail.txt"), 20896, nr + 1)
        log7 = synth_picklog(os.path.join(tmp, "picklog_consec_7trail.txt"), 20896, nr + 7)
        logs = synth_picklog(os.path.join(tmp, "picklog_consec_short.txt"), 20896, nr - 1)
        G["O synthetic pick log parses like picklog_w100.txt (24 fields, U32 -1)"] = (
            not LP.parse(log1)[1] and open(log1).readline().count("\t") == 23 and "4294967295" in open(log1).readline())
        p1 = tra_copy(CONSEC_RUN, os.path.join(tmp, "run_c_plus1"), lambda c: c + 1)
        p3 = tra_copy(CONSEC_RUN, os.path.join(tmp, "run_c_drop0"), drop=[0])
        p4 = tra_copy(CONSEC_RUN, os.path.join(tmp, "run_c_drop1000"), drop=[1000])
        new = {"(i) consecutive as is": (log1, CONSEC_RUN, "PASS"), "(ii) consecutive col0 + 1": (log1, p1, "FAIL"),
               "(iii) consecutive first pick without row": (log1, p3, "FAIL"), "(iv) consecutive middle pick without row": (log1, p4, "FAIL"),
               "(v) consecutive 7 trailing picks": (log7, CONSEC_RUN, "PASS"), "(vi) consecutive pick log shorter than rows": (logs, CONSEC_RUN, "FAIL")}
        for tag, (lg, rd, want) in new.items():
            one_case(tag, one, lg, rd, None, want)
        own_txt = lambda t: "OWN 대응 근거 부족" in (res[t]["why"] or "")                       # noqa: E731
        G["O (i): {0: 2540}, trailing 1 (23436), lag 0 on 2541"] = (s2("(i) consecutive as is")[H] == {0: 2540} and s2("(i) consecutive as is")["trailing_picks"] == 1
                                                                   and s2("(i) consecutive as is")["trailing_picked_first5"] == [23436]
                                                                   and res["(i) consecutive as is"]["step4"]["lag_pick_hist"] == {0: 2541})
        G["O (ii): {1: 2540}, OWN text, k 0 col0 1 picked 20896; old join would PASS (2540 matched)"] = (
            s2("(ii) consecutive col0 + 1")[H] == {1: 2540} and own_txt("(ii) consecutive col0 + 1") and ff("(ii) consecutive col0 + 1") == (0, 1, 20896, 20896)
            and s2("(ii) consecutive col0 + 1")["join_reference"]["rows_matched_in_order"] == 2540)
        G["O (iii): {1: 2539}, OWN text, k 0 col0 1 picked 20896, trailing 2; old join would PASS"] = (
            s2("(iii) consecutive first pick without row")[H] == {1: 2539} and own_txt("(iii) consecutive first pick without row")
            and ff("(iii) consecutive first pick without row") == (0, 1, 20896, 20896) and s2("(iii) consecutive first pick without row")["trailing_picks"] == 2
            and s2("(iii) consecutive first pick without row")["join_reference"]["rows_matched_in_order"] == 2539)
        G["O (iv): {0: 1000, 1: 1539}, OWN text, k 1000 col0 1001 picked 21896; old join would PASS"] = (
            s2("(iv) consecutive middle pick without row")[H] == {0: 1000, 1: 1539} and own_txt("(iv) consecutive middle pick without row")
            and ff("(iv) consecutive middle pick without row") == (1000, 1001, 20896, 21896)
            and s2("(iv) consecutive middle pick without row")["join_reference"]["rows_matched_in_order"] == 2539)
        G["O (v): {0: 2540}, trailing 7, first 5 23436..23440"] = (s2("(v) consecutive 7 trailing picks")[H] == {0: 2540}
                                                                  and s2("(v) consecutive 7 trailing picks")["trailing_picks"] == 7
                                                                  and s2("(v) consecutive 7 trailing picks")["trailing_picked_first5"] == list(range(23436, 23441)))
        G["O (vi): lines 2539 < rows 2540, OWN text, k 2539 (col0 2539, no pick), trailing 0"] = (
            s2("(vi) consecutive pick log shorter than rows")["log_lines"] == 2539 and own_txt("(vi) consecutive pick log shorter than rows")
            and ff("(vi) consecutive pick log shorter than rows") == (2539, 2539, 20896, None) and s2("(vi) consecutive pick log shorter than rows")["trailing_picks"] == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    G["O TEMP stand-ins removed"] = not os.path.exists(tmp)
    return G, res


if __name__ == "__main__":
    av = sys.argv[1:]
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    if "--dry" in av:
        G, res = dry()
        for k, v in G.items():
            print("GATE %-100s %s" % (k, "PASS" if v else "FAIL"), flush=True)
        bad = [k for k, v in G.items() if not v]
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
        sys.exit(1 if bad else 0)
    r = run(arg("--getbuff"), arg("--picklog"), arg("--run"), arg("--leg-json"))
    s = json.dumps(r, indent=1, default=str)
    print(s[:4000])
    if arg("--out"):
        open(arg("--out"), "w", encoding="utf-8").write(s)
    st = {"PASS": "PASS", "FAIL": "FAIL", "NOT RUN": "SKIP"}[r["verdict"]]
    print(P.result_line(P.make_result(1 if st == "PASS" else 0, 1 if st == "FAIL" else 0,
                                      None if st == "PASS" else ("%s: %s" % (r["verdict"], r["why"])), status=st)), flush=True)
    sys.exit(0 if st == "PASS" else 1)
