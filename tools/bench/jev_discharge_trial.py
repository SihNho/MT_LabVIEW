r"""jev_discharge_trial.py - MEASURE, do not adopt: can Jev tell whether an archived peer review already covers a
new failing run? (docs/jev-integration-plan.md insertion #1, "실패 예측 리뷰 면제", user 2026-09-22.)

NO LabVIEW IS TOUCHED. It reads tools/bench/*.log and archive/peer/*.md off disk and makes HTTPS calls to
api.typesafe.ai through tools/jev.py. No COM, no VISA, no motor, no camera, no GUI, no .vi is opened.

WHAT ALREADY EXISTS (checked before writing): tools/jev.py (transport, key, ledger, summarise_failure, verdict),
tools/bench/jev_trial.py (the measured 40-pair trial of insertion #3 - its pattern is followed, its summariser is
now in jev.py and is REUSED), tools/bench/jev_gate.py (this cycle: the shared question + review summariser, so the
trial measures EXACTLY what the gate will ask), tools/logclass.py, tools/hooks/guard_peer.py (review_quality).
No existing review-coverage measurement was found under tools/ or tools/bench/.

THE LABELLED SET. Every failing build/diagnostic log of 2026-09-21..22 (rc != 0 or TIMEOUT, peer_/priorart_/
retro/cycle_/selftest_ excluded: 32 logs) and every archived `-Role hypothesis`, outcome ANSWERED exchange of the
same two days (26 with a Question section that names a log). A pair is labelled:

  SAME  - the review's `## Question` section names that log's failure: the log itself, or its script and the very
          gate line that failed. 18 of the 20 SAME pairs are that mechanical match.
  DIFF  - it does not. 12 of the 20 DIFF pairs are manifestly different subjects; 8 are NEAR MISSES chosen on
          purpose (same checker different gate, same stage different row, adjacent runs of one script), because
          only those can separate a model from a filename match.

FOUR pairs are labelled BY READING rather than by the name rule; each carries its reason inline, and the four are
reported separately so the reading is visible instead of buried:
  * build_d1_m3a3_run2.log x c75-m3a3-run1-failpred  -> SAME (the live case: run 2's first FAIL line IS that
    review's PREDICTION 1, verbatim - FlatSequence #681 does not resolve to a Nodes[] terminal table).
  * diag_s58_boolcarrier.log x c58-delete-execstate0  -> SAME (run 0 and run 1 fail on the identical gate C1 B3b).
  * diag_c62_s3b_build.log x c62-row1-precond         -> SAME (rows and build are one route failing at one
    precondition - the reading already recorded in tools/bench/jev_trial.py's HARD block).
  * diag_c67_addsr.log x c67-addsr-noop               -> DIFF (that review is about diag_c67_m3a's no-op read;
    addsr fails on class counts not changing, the NEXT question).

PREDICTION CONTRACT (written before any call; the run is a FAILED PREDICTION if these do not hold):
  P1 The pair set is written to tools/bench/jev_discharge_set.json BEFORE the first API call.
  P2 Exactly len(PAIRS) <= 40 calls, one noul question each.
  P3 Every call returns a noul probability in [0,1], or is recorded as an ERROR pair and excluded from the scores.
  P4 The key is never printed, logged, written to JSON or passed as an argument.
  P5 The 8 NEAR-MISS DIFF pairs are the ones that carry the evidence; the report states that next to the numbers.
"""
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev            # noqa: E402
import jev_gate       # noqa: E402
import logclass       # noqa: E402

BENCH = HERE
PEER = os.path.join(ROOT, "archive", "peer")
OUT_JSON = os.path.join(BENCH, "jev_discharge_set.json")
MAX_CALLS = 40
THRESHOLD = 0.5
SWEEP = (0.70, 0.80, 0.85, 0.90)

R = {
    "R1": "2026-09-21-c58-boolwire-dangling.md",
    "R2": "2026-09-21-c58-delete-execstate0.md",
    "R3": "2026-09-21-c60-cast-seed-execstate0.md",
    "R4": "2026-09-21-c60-ia-count-gate.md",
    "R5": "2026-09-21-c60-l0-readback-none.md",
    "R6": "2026-09-21-c61-localpn-execstate0.md",
    "R7": "2026-09-21-c62-astcheck7.md",
    "R8": "2026-09-21-c62-ctwire.md",
    "R9": "2026-09-21-c62-localplacement.md",
    "R10": "2026-09-21-c62-movein-es0.md",
    "R11": "2026-09-21-c62-row1-precond.md",
    "R12": "2026-09-21-c64-astgate3.md",
    "R13": "2026-09-21-c64-row1-wirecount-k2.md",
    "R15": "2026-09-21-c65-astcheck-gate7.md",
    "R16": "2026-09-21-c65-row2-indicator.md",
    "R17": "2026-09-21-c65-testa-timeout.md",
    "R18": "2026-09-21-c66-m3-execstate0.md",
    "R19": "2026-09-21-c66-m3-movelocals.md",
    "R21": "2026-09-21-c67-addsr-noop.md",
    "R22": "2026-09-21-c67-addsr-opvi.md",
    "R23": "2026-09-22-c74-gate10-arity.md",
    "R24": "2026-09-22-c75-m3a3-run1-failpred.md",
}

# (block, log, review key, label SAME?, reason when the label was set by READING)
PAIRS = [
    # ---------------- SAME by the name rule (17)
    ("SAME", "diag_s58_boolcarrier_run2.log", "R1", True, ""),
    ("SAME", "diag_s58_boolcarrier_run1.log", "R2", True, ""),
    ("SAME", "diag_s3b_l0_localname_v2.log", "R3", True, ""),
    ("SAME", "diag_s3b_l0_localname.log", "R4", True, ""),
    ("SAME", "diag_s3b_l0_createlocal.log", "R5", True, ""),
    ("SAME", "diag_c61_localdir_write.log", "R6", True, ""),
    ("SAME", "c62f_astcheck.log", "R7", True, ""),
    ("SAME", "diag_c62_branch.log", "R8", True, ""),
    ("SAME", "diag_c62_s3b_build.log", "R9", True, ""),
    ("SAME", "diag_c62_s3b_movein.log", "R10", True, ""),
    ("SAME", "diag_c62_s3b_rows.log", "R11", True, ""),
    ("SAME", "c63_astcheck.log", "R12", True, ""),
    ("SAME", "diag_c64_s3b_row1.log", "R13", True, ""),
    ("SAME", "c65_astcheck.log", "R15", True, ""),
    ("SAME", "diag_c66b_s3b_m3.log", "R18", True, ""),
    ("SAME", "diag_c67_addsr.log", "R22", True, ""),
    ("SAME", "build_d1_m3a3.log", "R24", True, ""),

    # ---------------- SAME by READING (3)
    ("READ", "build_d1_m3a3_run2.log", "R24", True,
     "THE LIVE CASE. Run 2's first FAIL line is 'P0 ROW D's SINK RESOLVED - wire # appears EXACTLY ONCE on "
     "FlatSequence #'s terminal table ... FAILED PREDICTION', which is verbatim PREDICTION 1 of this review "
     "(dispatched for run 1). STATUS.md records Row D as deferred to M3a-3b on exactly that reviewed ground, so "
     "a second review would re-ask a disposed question."),
    ("READ", "diag_s58_boolcarrier.log", "R2", True,
     "run 0 and run 1 of diag_s58_boolcarrier.py are the same bytes (39,566 each) and stop at the identical gate "
     "C1 B3b, 'ExecState after the delete == 1 -> 0 (PREDICTED RISK (v))' - the review names run 1."),
    ("READ", "diag_c62_s3b_build.log", "R11", True,
     "rows and build are one route failing at one precondition - the source is addressable only on an inner "
     "diagram - the reading already recorded in tools/bench/jev_trial.py's HARD block for this pair of logs."),

    # ---------------- DIFF, NEAR MISS (8): these carry the evidence (P5)
    ("NEAR", "c65_astcheck.log", "R12", False,
     "same checker c60c_astcheck.py, different gate: R12 attacks gate 3 (allow_broken never passed), c65 stops "
     "at gate 7 (move_in neither imported nor called) in a different recipe."),
    ("NEAR", "c63_astcheck.log", "R15", False,
     "the mirror of the pair above: R15 is the gate-7 review, c63 is the gate-3 failure."),
    ("NEAR", "c74_gate10_m3a2.log", "R15", False,
     "same checker again: gate 10 is a %-format validity finding on one literal; R15 is gate 7's move_in rule."),
    ("NEAR", "c62f_astcheck.log", "R12", False,
     "c62f is in the gate-7 family that R15 names; R12 is the gate-3 review."),
    ("NEAR", "diag_c65_s3b_row2b.log", "R16", False,
     "R16 attacks row2's failure (a source uid that does not resolve to a live Traverse index); row2b fails "
     "because the ControlTerminal census and the diagram's Nodes[] list do not intersect at all."),
    ("NEAR", "diag_c66_s3b_m3.log", "R18", False,
     "R18 is the ExecState-0 review of c66b, which got all seven objects moved; c66 failed earlier, on a node "
     "sitting at an unexpected position."),
    ("NEAR", "diag_c66b_s3b_m3.log", "R19", False,
     "the mirror: R19 attacks c66's move set and abort clause; c66b's failure is the later ExecState 0."),
    ("NEAR", "diag_c67_addsr.log", "R21", False,
     "R21 is about diag_c67_m3a's no-op shift-register READ (OpShiftRegs_v0 property-node errors); addsr fails "
     "gate L1c because no whole-VI class count changed after add_shift_reg - the next question, not the same."),

    # ---------------- DIFF, manifestly different subjects (12)
    ("DIFF", "diag_s58_boolcarrier_run2.log", "R6", False, ""),
    ("DIFF", "diag_c61_localdir_write.log", "R1", False, ""),
    ("DIFF", "diag_c62_branch.log", "R13", False, ""),
    ("DIFF", "diag_c64_s3b_row1.log", "R8", False, ""),
    ("DIFF", "c62f_astcheck.log", "R18", False, ""),
    ("DIFF", "diag_c66b_s3b_m3.log", "R7", False, ""),
    ("DIFF", "diag_s3b_l0_createlocal.log", "R22", False, ""),
    ("DIFF", "diag_c67_addsr.log", "R5", False, ""),
    ("DIFF", "diag_c64_row1_testa.log", "R23", False, ""),
    ("DIFF", "c74_gate10_m3a2.log", "R17", False, ""),
    ("DIFF", "build_d1_m3a3_run2.log", "R11", False, ""),
    ("DIFF", "diag_c66c_coercion.log", "R3", False, ""),
]


def build_rows():
    missing = []
    for _, log, rk, _, _ in PAIRS:
        if not os.path.isfile(os.path.join(BENCH, log)):
            missing.append(log)
        if not os.path.isfile(os.path.join(PEER, R[rk])):
            missing.append(R[rk])
    if missing:
        raise RuntimeError("missing file(s): " + ", ".join(sorted(set(missing))))
    bad = [log for _, log, _, _, _ in PAIRS if not logclass.is_build_log(log)]
    if bad:
        raise RuntimeError("non-build log(s) in the set: " + ", ".join(sorted(set(bad))))
    rows = []
    for block, log, rk, label, why in PAIRS:
        rows.append(dict(block=block, log=log, review=R[rk], label=bool(label), reason=why,
                         summary_failure=jev.summarise_failure(os.path.join(BENCH, log)),
                         summary_review=jev_gate.summarise_review(os.path.join(PEER, R[rk])),
                         p=None, latency_s=None, error=None))
    return rows


def acc(rows, thr):
    if not rows:
        return float("nan"), 0, 0
    n = sum(1 for r in rows if (r["p"] >= thr) == r["label"])
    return n / len(rows), n, len(rows)


def report(rows, title):
    scored = [r for r in rows if r["p"] is not None]
    n_err = sum(1 for r in rows if r["p"] is None)
    print("\n" + "=" * 78)
    print("%s  (%d scored, %d error(s))" % (title, len(scored), n_err))
    print("=" * 78)
    if not scored:
        print("  nothing scored")
        return {}
    print("%-8s %-6s %s" % ("block", "n", "accuracy at 0.50"))
    summary = {}
    for blk in ("SAME", "READ", "NEAR", "DIFF", "ALL"):
        rs = scored if blk == "ALL" else [r for r in scored if r["block"] == blk]
        a, n, t = acc(rs, THRESHOLD)
        summary[blk] = dict(n=t, acc=a, correct=n)
        if t:
            print("%-8s %-6d %5.1f%% (%d/%d)" % (blk, t, a * 100, n, t))
    print("\nP5: the NEAR block (same tool / adjacent run / neighbouring row) is what separates a judge from a")
    print("    filename match. The DIFF block is easy by construction and is reported only for balance.")

    brier = sum((r["p"] - (1.0 if r["label"] else 0.0)) ** 2 for r in scored) / len(scored)
    hard = [r for r in scored if r["block"] in ("READ", "NEAR")]
    brier_hard = (sum((r["p"] - (1.0 if r["label"] else 0.0)) ** 2 for r in hard) / len(hard)) if hard else None
    lat = [r["latency_s"] for r in scored if r["latency_s"]]
    print("\nBrier: all %.4f ; READ+NEAR only %s" % (
        brier, ("%.4f" % brier_hard) if brier_hard is not None else "n/a"))
    if lat:
        print("latency: mean %.2fs  min %.2fs  max %.2fs  over %d calls" % (
            sum(lat) / len(lat), min(lat), max(lat), len(lat)))

    print("\n--- THRESHOLD SWEEP (a gate that ALLOWS at p >= t; precision is what a wrong allow costs) ---")
    print("%-8s %-10s %-10s %-10s %-10s %s" % ("t", "allowed", "true-allow", "precision", "recall", "accuracy"))
    sweep = {}
    for t in SWEEP:
        allowed = [r for r in scored if r["p"] >= t]
        tp = sum(1 for r in allowed if r["label"])
        pos = sum(1 for r in scored if r["label"])
        prec = (tp / len(allowed)) if allowed else float("nan")
        rec = (tp / pos) if pos else float("nan")
        a, _, _ = acc(scored, t)
        sweep["%.2f" % t] = dict(allowed=len(allowed), true_allow=tp, precision=prec, recall=rec, accuracy=a)
        print("%-8.2f %-10d %-10d %-10s %-10s %.3f" % (
            t, len(allowed), tp, "%.3f" % prec if allowed else "n/a",
            "%.3f" % rec if pos else "n/a", a))

    print("\n--- DISAGREEMENTS WITH THE LABEL (at 0.50) ---")
    dis = [r for r in scored if (r["p"] >= THRESHOLD) != r["label"]]
    for r in dis:
        print("  %-5s %-32s %-40s label=%-4s p=%.3f" % (
            r["block"], r["log"][:32], r["review"][:40], "SAME" if r["label"] else "DIFF", r["p"]))
    if not dis:
        print("  (none)")
    print("\n--- WHAT THE WIRED GATE WOULD DO (allow at p >= %.2f) ---" % jev_gate.DISCHARGE_P)
    wrong_allow = [r for r in scored if r["p"] >= jev_gate.DISCHARGE_P and not r["label"]]
    print("  reviews that would DISCHARGE a failure they do not cover: %d" % len(wrong_allow))
    for r in wrong_allow:
        print("    %-5s %-32s %-40s p=%.3f" % (r["block"], r["log"][:32], r["review"][:40], r["p"]))
    return dict(summary=summary, brier=brier, brier_hard=brier_hard, sweep=sweep,
                n_disagree=len(dis), n_wrong_allow=len(wrong_allow),
                latency_mean_s=(sum(lat) / len(lat)) if lat else None)


def main():
    print("=== jev_discharge_trial: does an archived review already cover a new failure? (plan row #1) ===")
    print("NO LabVIEW is touched. Reads tools/bench/*.log + archive/peer/*.md, HTTPS to api.typesafe.ai.\n")
    if len(PAIRS) > MAX_CALLS:
        print("  FAIL  setup: %d pairs exceeds the %d-call cap" % (len(PAIRS), MAX_CALLS))
        return 1
    rows = build_rows()
    print("PAIRS: %d over %d distinct failing logs and %d distinct reviews" % (
        len(rows), len({r["log"] for r in rows}), len({r["review"] for r in rows})))
    print("  SAME %d (name rule) | READ %d (labelled by reading) | NEAR %d (near-miss DIFF) | DIFF %d" % (
        sum(r["block"] == "SAME" for r in rows), sum(r["block"] == "READ" for r in rows),
        sum(r["block"] == "NEAR" for r in rows), sum(r["block"] == "DIFF" for r in rows)))
    empty = [r for r in rows if not r["summary_failure"] or not r["summary_review"]]
    if empty:
        print("  FAIL  setup: %d pair(s) have an empty summary: %s" % (
            len(empty), ", ".join(r["log"] for r in empty)))
        return 1
    print("  PASS  every pair has both summaries")
    json.dump({"stage": "pairs-only (pre-API)", "pairs": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("  PASS  P1 pair set written BEFORE any API call -> %s\n" % os.path.relpath(OUT_JSON, ROOT))

    print("--- pairs labelled by READING, with their reasons ---")
    for r in rows:
        if r["reason"]:
            print("  %-5s %-32s %-40s label=%s\n      %s" % (
                r["block"], r["log"][:32], r["review"][:40], "SAME" if r["label"] else "DIFF",
                " ".join(r["reason"].split())))
    print()

    if not jev.get_key():
        print("  FAIL  TYPESAFE_API_KEY is not readable. Pairs are on disk; re-run when it is visible.")
        json.dump({"stage": "pairs-only (no key)", "pairs": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
        return 2

    consec_err = 0
    for i, r in enumerate(rows, 1):
        t0 = time.time()
        p, err = jev_gate.covers_failure(r["summary_failure"], r["summary_review"], "trial-discharge")
        r["latency_s"] = round(time.time() - t0, 2)
        if p is None:
            r["error"] = err
            consec_err += 1
            print("  [%2d/%d] %-5s ERROR %s" % (i, len(rows), r["block"], str(err)[:100]))
            if consec_err >= 3:
                print("\nABORT: 3 consecutive failures - the request shape or the credential is wrong.")
                break
            continue
        consec_err = 0
        r["p"] = p
        ok = (p >= THRESHOLD) == r["label"]
        print("  [%2d/%d] %-5s %-30s %-38s label=%-4s p=%.3f %s (%.1fs)" % (
            i, len(rows), r["block"], r["log"][:30], r["review"][:38],
            "SAME" if r["label"] else "DIFF", p, "ok" if ok else "XX", r["latency_s"]))

    res = report(rows, "RESULTS - review-covers-failure")
    json.dump({"stage": "complete", "threshold": THRESHOLD, "discharge_p": jev_gate.DISCHARGE_P,
               "results": res, "pairs": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("\nraw -> %s" % os.path.relpath(OUT_JSON, ROOT))
    n_err = sum(1 for r in rows if r["p"] is None)
    print("\n=== jev_discharge_trial: %d/%d scored, %d error(s) ===" % (len(rows) - n_err, len(rows), n_err))
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
