r"""jev_priorart_trial.py - MEASURE, do not adopt: can Jev tell that a planned step has ALREADY been prior-art
reviewed? (docs/jev-integration-plan.md insertion #6, "사전 조사 재질의 방지", user 2026-09-22.)

NO LabVIEW IS TOUCHED. Reads docs/cycle27-plan.md and archive/peer/*priorart*.md off disk; HTTPS through
tools/jev.py only.

WHAT ALREADY EXISTS (checked before writing): tools/jev.py; tools/bench/jev_gate.py (this cycle - the shared
question and review summariser, so the trial measures exactly what the advisory will ask);
tools/prior_art_review.py (the dispatcher being instrumented). No duplicate-question detector existed.

THE LABELLED SET. 10 planned steps, each one sentence as a session would state it when about to dispatch a
prior-art review, drawn from docs/cycle27-plan.md's Pre-decided items and the stage names STATUS.md uses; and 12
archived prior-art reviews that carry an explicit "WHAT IS UNDER REVIEW" header (reviews that attach the WHOLE
plan document instead - s0-gamma1, c60-localname-decomposition, d1-s3a-recipe, d1-s1-stage, s0-closeref - are
EXCLUDED on purpose: their question text does not identify a step, so any label for them would be a guess about
what the reviewer inferred rather than a fact about what was asked).

  SAME 11 | NEAR-MISS DIFF 8 (neighbouring stage, mirror direction, the same recipe's other edit round) | DIFF 11.

THE STEP SENTENCES ARE WRITTEN BEFORE THE REVIEWS ARE READ IN PAIRS, and deliberately do NOT quote the review's
own wording - a step stated in the words of its own review would measure string overlap, not judgement.

PREDICTION CONTRACT:
  P1 the set is written to tools/bench/jev_priorart_set.json BEFORE the first API call
  P2 exactly len(PAIRS) <= 30 calls, one noul each
  P3 an unparseable answer is an ERROR pair, excluded from the scores
  P4 the key is never printed, logged, written or passed as an argument
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
from jev_discharge_trial import acc, THRESHOLD, SWEEP     # noqa: E402  - one scoring definition, not two

PEER = os.path.join(ROOT, "archive", "peer")
OUT_JSON = os.path.join(HERE, "jev_priorart_set.json")
MAX_CALLS = 30

STEPS = {
    "B1": "S0, the reference-hygiene repair of the traverse ops, has failed twice at the same place. Split it "
          "into sub-steps that each save an intermediate artefact, and write that one-page decomposition table "
          "before any sub-step script is cut.",
    "B2": "D1 stage S2 as tools/recipes/stage_d1_s2_loops.py: start from claudeDev\\D1_s1_copy.vi, create three "
          "empty While loops on Diagram #686 and scaffold each one, saving the result as D1_s2_loops.vi.",
    "B3": "D1 stage S2 as tools/recipes/stage_d1_s2.py, the delete + loops + re-drop written as one stage whose "
          "first phase is a measurement that edits nothing (docs/cycle27-plan.md Pre-decided 30).",
    "B4": "D1 stage S3: move the whole 1.5 FOCUS node set into loop a and re-wire it in one saved stage, the "
          "atomic shape Pre-decided 37(g) defines, as tools/recipes/stage_d1_s3_focus.py.",
    "B5": "D1 stage S3a: create two free-standing front-panel focus indicators (Pre-decided 46(a)+(d)) as the "
          "first half of the transport, with a new recipe that does not exist yet.",
    "B6": "Stage M3a-1 of the D1 restructure: the FIRST version of tools/recipes/build_d1_m3a1.py, which builds "
          "one saved intermediate from the read-only bed claudeDev\\D1_s3b_row2_20260921_160311.vi.",
    "B6b": "The edit round on tools/recipes/build_d1_m3a1.py that STATUS.md's NEXT authorises as exactly three "
           "changes, made in place by the runner-triggered firefighter session, ordered prior-art -> astcheck -> "
           "build.",
    "B7": "Stage M3a-2: re-source the two INITIAL-VALUE rows onto the new While loop's LEFT shift registers, with "
          "tools/recipes/build_d1_m3a2.py, which is written and has passed the static gate but not been launched.",
    "B8": "Stage M3a-3: re-source the two DOWNSTREAM CONSUMERS - Global #7202 'Global motor pos.vi' terminal 0 and "
          "FlatSequenceInnerTunnel #7468 - onto the new loop's RIGHT shift registers, starting from "
          "claudeDev\\D1_s3b_m3a2_20260922_023029.vi.",
    "B10": "D1 route B, run 10: launch tools/recipes/build_d1_routeb_v7.py, cut byte-exact from v6 with one "
           "change, to restructure the loops inside a copy of the original VI in a single script.",
}

P = {
    "P1": "2026-09-19-priorart-s0-decomp.md",
    "P2": "2026-09-20-priorart-d1-s2-loops.md",
    "P3": "2026-09-20-priorart-d1-s2-stage.md",
    "P4": "2026-09-20-priorart-d1-s2-stage-r2.md",
    "P5": "2026-09-20-priorart-d1-s3-focus.md",
    "P6": "2026-09-20-priorart-d1-s3a-focus-ind.md",
    "P7": "2026-09-21-priorart-c68-m3a1.md",
    "P9": "2026-09-21-priorart-c71-m3a1.md",
    "P10": "2026-09-22-priorart-priorart-c74-m3a2.md",
    "P11": "2026-09-22-priorart-c75-m3a3.md",
    "P14": "2026-09-19-priorart-d1-routeb-run10.md",
}

# (block, step key, review key, label ALREADY-ANSWERED?, reason when set by reading)
PAIRS = [
    ("SAME", "B1", "P1", True, ""),
    ("SAME", "B2", "P2", True, ""),
    ("SAME", "B3", "P3", True, ""),
    ("READ", "B3", "P4", True,
     "r2 is explicitly the SECOND prior-art review of the same recipe tools/recipes/stage_d1_s2.py on different "
     "bytes; the step is unchanged, so the step's question is answered there too."),
    ("SAME", "B4", "P5", True, ""),
    ("SAME", "B5", "P6", True, ""),
    ("SAME", "B6", "P7", True, ""),
    ("READ", "B6b", "P9", True,
     "c71-m3a1 states in its own first line that it reviews ONE EDIT ROUND on build_d1_m3a1.py performed by the "
     "cycle-57 firefighter under a three-change authorisation, ordered prior-art -> astcheck -> build."),
    ("SAME", "B7", "P10", True, ""),
    ("SAME", "B8", "P11", True, ""),
    ("SAME", "B10", "P14", True, ""),

    ("NEAR", "B4", "P6", False,
     "S3 moves the 1.5 FOCUS node set into a loop; S3a creates two free-standing indicators. Adjacent stages of "
     "one transport, different work - and S3a's own review says it REPLACES the S3 review for its work."),
    ("NEAR", "B5", "P5", False, "the mirror of the pair above."),
    ("READ", "B6", "P9", False,
     "P9 reviews the three-change EDIT ROUND; B6 is the first version of the same file. The 2026-09-19 split rule "
     "makes these two separate reviewed steps on purpose, which is why c68/c70/c71 exist as three files."),
    ("READ", "B6b", "P7", False, "the mirror: c68 reviewed the predecessor bytes, not the authorised edit round."),
    ("NEAR", "B7", "P11", False, "M3a-2 is the two initial-value rows on the LEFT registers; M3a-3 is the two "
                                 "downstream consumers on the RIGHT registers."),
    ("NEAR", "B8", "P10", False, "the mirror of the pair above."),
    ("NEAR", "B7", "P7", False, "M3a-1 built the registers; M3a-2 sources the initial-value rows onto them."),
    ("NEAR", "B8", "P7", False, "M3a-1 built the registers; M3a-3 re-sources the downstream consumers."),

    ("DIFF", "B1", "P2", False, ""),
    ("DIFF", "B1", "P11", False, ""),
    ("DIFF", "B1", "P5", False, ""),
    ("DIFF", "B2", "P5", False, ""),
    ("DIFF", "B2", "P6", False, ""),
    ("DIFF", "B4", "P1", False, ""),
    ("DIFF", "B5", "P10", False, ""),
    ("DIFF", "B6", "P11", False, ""),
    ("DIFF", "B10", "P6", False, ""),
    ("DIFF", "B10", "P11", False, ""),
    ("DIFF", "B3", "P14", False, ""),
]


def main():
    print("=== jev_priorart_trial: is this step already prior-art reviewed? (plan row #6) ===")
    print("NO LabVIEW is touched. Reads archive/peer/*priorart*.md; HTTPS to api.typesafe.ai.\n")
    if len(PAIRS) > MAX_CALLS:
        print("  FAIL  setup: %d pairs exceeds the %d-call cap" % (len(PAIRS), MAX_CALLS))
        return 1
    missing = [P[rk] for _, _, rk, _, _ in PAIRS if not os.path.isfile(os.path.join(PEER, P[rk]))]
    if missing:
        print("  FAIL  setup: missing review(s): %s" % ", ".join(sorted(set(missing))))
        return 1
    rows = []
    for block, sk, rk, label, why in PAIRS:
        rows.append(dict(block=block, step=sk, step_text=STEPS[sk], review=P[rk], label=bool(label), reason=why,
                         summary_review=jev_gate.summarise_review(os.path.join(PEER, P[rk])),
                         p=None, latency_s=None, error=None))
    print("PAIRS: %d over %d steps and %d reviews (SAME %d | READ %d | NEAR %d | DIFF %d)" % (
        len(rows), len({r["step"] for r in rows}), len({r["review"] for r in rows}),
        sum(r["block"] == "SAME" for r in rows), sum(r["block"] == "READ" for r in rows),
        sum(r["block"] == "NEAR" for r in rows), sum(r["block"] == "DIFF" for r in rows)))
    empty = [r for r in rows if not r["summary_review"]]
    if empty:
        print("  FAIL  setup: %d review summary/summaries empty" % len(empty))
        return 1
    print("  PASS  every review summarised")
    json.dump({"stage": "pairs-only (pre-API)", "pairs": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("  PASS  P1 set written BEFORE any API call -> %s\n" % os.path.relpath(OUT_JSON, ROOT))

    if not jev.get_key():
        print("  FAIL  TYPESAFE_API_KEY is not readable. Set is on disk; re-run when it is visible.")
        return 2

    consec_err = 0
    for i, r in enumerate(rows, 1):
        t0 = time.time()
        p, err = jev_gate.answers_step(r["step_text"], r["summary_review"], "trial-priorart")
        r["latency_s"] = round(time.time() - t0, 2)
        if p is None:
            r["error"] = err
            consec_err += 1
            print("  [%2d/%d] %-5s ERROR %s" % (i, len(rows), r["block"], str(err)[:100]))
            if consec_err >= 3:
                print("\nABORT: 3 consecutive failures - request shape or credential is wrong.")
                break
            continue
        consec_err = 0
        r["p"] = p
        ok = (p >= THRESHOLD) == r["label"]
        print("  [%2d/%d] %-5s %-5s %-40s label=%-4s p=%.3f %s (%.1fs)" % (
            i, len(rows), r["block"], r["step"], r["review"][:40],
            "YES" if r["label"] else "NO", p, "ok" if ok else "XX", r["latency_s"]))

    scored = [r for r in rows if r["p"] is not None]
    n_err = len(rows) - len(scored)
    print("\n" + "=" * 78)
    print("RESULTS - review-answers-step  (%d scored, %d error(s))" % (len(scored), n_err))
    print("=" * 78)
    summary = {}
    if scored:
        print("%-8s %-6s %s" % ("block", "n", "accuracy at 0.50"))
        for blk in ("SAME", "READ", "NEAR", "DIFF", "ALL"):
            rs = scored if blk == "ALL" else [r for r in scored if r["block"] == blk]
            a, n, t = acc(rs, THRESHOLD)
            summary[blk] = dict(n=t, acc=a, correct=n)
            if t:
                print("%-8s %-6d %5.1f%% (%d/%d)" % (blk, t, a * 100, n, t))
        brier = sum((r["p"] - (1.0 if r["label"] else 0.0)) ** 2 for r in scored) / len(scored)
        hard = [r for r in scored if r["block"] in ("READ", "NEAR")]
        brier_hard = (sum((r["p"] - (1.0 if r["label"] else 0.0)) ** 2 for r in hard) / len(hard)) if hard else None
        lat = [r["latency_s"] for r in scored if r["latency_s"]]
        print("\nBrier: all %.4f ; READ+NEAR only %s" % (
            brier, ("%.4f" % brier_hard) if brier_hard is not None else "n/a"))
        if lat:
            print("latency: mean %.2fs  min %.2fs  max %.2fs over %d calls" % (
                sum(lat) / len(lat), min(lat), max(lat), len(lat)))
        print("\n--- THRESHOLD SWEEP (an advisory that FIRES at p >= t) ---")
        print("%-8s %-10s %-10s %-10s %-10s %s" % ("t", "fired", "true-dup", "precision", "recall", "accuracy"))
        sweep = {}
        for t in SWEEP:
            fired = [r for r in scored if r["p"] >= t]
            tp = sum(1 for r in fired if r["label"])
            pos = sum(1 for r in scored if r["label"])
            prec = (tp / len(fired)) if fired else float("nan")
            rec = (tp / pos) if pos else float("nan")
            a, _, _ = acc(scored, t)
            sweep["%.2f" % t] = dict(fired=len(fired), true_dup=tp, precision=prec, recall=rec, accuracy=a)
            print("%-8.2f %-10d %-10d %-10s %-10s %.3f" % (
                t, len(fired), tp, "%.3f" % prec if fired else "n/a", "%.3f" % rec if pos else "n/a", a))
        print("\n--- DISAGREEMENTS WITH THE LABEL (at 0.50) ---")
        dis = [r for r in scored if (r["p"] >= THRESHOLD) != r["label"]]
        for r in dis:
            print("  %-5s %-5s %-40s label=%-4s p=%.3f  %s" % (
                r["block"], r["step"], r["review"][:40], "YES" if r["label"] else "NO", r["p"],
                " ".join(r["reason"].split())[:90]))
        if not dis:
            print("  (none)")
        wrong = [r for r in scored if r["p"] >= jev_gate.DUP_P and not r["label"]]
        print("\n--- WHAT THE WIRED ADVISORY WOULD DO (fire at p >= %.2f; it BLOCKS NOTHING) ---" % jev_gate.DUP_P)
        print("  steps it would wrongly call a duplicate: %d" % len(wrong))
        for r in wrong:
            print("    %-5s %-40s p=%.3f" % (r["step"], r["review"][:40], r["p"]))
        json.dump({"stage": "complete", "summary": summary, "brier": brier, "brier_hard": brier_hard,
                   "sweep": sweep, "n_wrong_fire": len(wrong), "pairs": rows},
                  open(OUT_JSON, "w", encoding="utf-8"), indent=1)
    print("\nraw -> %s" % os.path.relpath(OUT_JSON, ROOT))
    print("\n=== jev_priorart_trial: %d/%d scored, %d error(s) ===" % (len(scored), len(rows), n_err))
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
