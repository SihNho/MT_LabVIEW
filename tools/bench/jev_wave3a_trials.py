r"""jev_wave3a_trials.py - the THIRD wave of docs/jev-integration-plan.md, measured in ONE run, one log, one
notification (CLAUDE.md section 3, "one batch = one runner"). Two changes were made today, both user-approved
2026-09-22 ("전부 적용해보자"), and this file measures both:

  (1) ONE REVIEW PER ROW PER CYCLE - a RULE CHANGE in tools/hooks/guard_peer.py: on the path that was about to
      BLOCK, an accepted review younger than 6 h that NAMES the failing log's own script releases the build,
      with no model call. Measured here on the record: how many of the reviews actually bought on 2026-09-21
      and 2026-09-22 this rule would have made unnecessary.
  (2) DRIFT AGAINST THE WHOLE NEXT - tools/jev_drift.py now hands the model the entire `## NEXT` section
      instead of the single first-act bullet, and asks "any act this NEXT orders or permits". Measured by
      re-running the SAME 31 labelled commands (tools/bench/jev_drift_set.json) that gave 77.4 % / Brier 0.181
      / 5 false alarms out of 18 on-task commands under the narrow question.

PREDICTION CONTRACT (written before the run):
  T1  the four self-tests all end rc=0                                          -> GATED
  T1b  and at their recorded sizes: samerow >= 13 rows, jev 17/0, ladder 21/0, guard_bash 11/0  -> GATED
  T2  the same-row rule's avoided-review count over 2026-09-21..22 is REPORTED with the file list -> REPORTED
  T3  every labelled command gets a consensus probability back (31/31)          -> GATED
  T4  accuracy under the new question, against BOTH label sets, is REPORTED     -> REPORTED, not gated
  T5  the 4 `sequel` commands (a later act of the SAME hand-off) now read on-task -> REPORTED
  T6  Jev spend for this run stays under $0.05 (the caller's budget)            -> GATED
  ⚠️ NOTHING HERE TOUCHES LabVIEW, COM, a .vi, or a motor. It runs self-tests, reads files and calls jev.ask.

ON THE TWO LABEL SETS (T4). The set's own labelling rule says, in writing, that a later act the SAME hand-off
defers ("THEN D-2 ...") was labelled OFF-TASK *because that was the literal question the gate asked*. The
question changed today, so those labels describe a question nobody asks any more. Both numbers are printed:
`original` (the file's labels, comparable with the 77.4 % on record) and `adjusted` (items whose own `why`
field says the act belongs to this same hand-off, flipped to on-task). The flip is mechanical - it is driven
by phrases in the set's `why` text, listed in ADJUST_PHRASES below, never by re-reading the commands - and
every disagreement is printed so the judgement session can see what moved.

PRIOR ART CHECKED before writing (CLAUDE.md, "check what already exists"):
  tools/bench/jev_wave2b_trials.py - the second-wave trial. This file copies its shape (set file -> pmap ->
                     accuracy / Brier / disagreement list) and re-implements none of its logic; its drift
                     section stays as the archived measurement of the OLD question.
  tools/jev.py     - transport, ledger, consensus (ask_n), unknown band. Not re-implemented.
  tools/jev_drift.py, tools/hooks/guard_peer.py - the two modules under test; the questions and the rule live
                     THERE, not here.
  tools/bench/selftest_guard_peer_{jev,ladder,samerow}.py, selftest_guard_bash_jev.py - the four self-tests,
                     run as subprocesses rather than re-implemented.
"""
import concurrent.futures as cf
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, HERE)
import jev              # noqa: E402
import jev_drift as jd  # noqa: E402
import guard_peer       # noqa: E402

DRIFT_SET = os.path.join(HERE, "jev_drift_set.json")
OUT = os.path.join(HERE, "jev_wave3a_trials.json")
MARKER = os.path.join(ROOT, "tools", "hooks", "material_marker.log")
PEER = os.path.join(ROOT, "archive", "peer")
BUDGET_USD = 0.05
USD_PER_MTOK_IN = 0.0427        # measured: 585,940 input tokens over the first 326 calls cost $0.025
SAMPLES = 5
OLD_ACC, OLD_FALSE_ALARMS, OLD_BRIER = 0.774, "5/18", 0.181

# The window the user named for the avoided-review count.
WIN_FROM = time.mktime((2026, 9, 21, 0, 0, 0, 0, 0, -1))
WIN_TO = time.mktime((2026, 9, 23, 0, 0, 0, 0, 0, -1))

# Mechanical relabel (see the module docstring): an item whose own `why` says the act belongs to the SAME
# hand-off. `same ...` inherits from the item above it, because the set writes retries as "same X, retried".
ADJUST_PHRASES = ("the next's", "defers", "past the first", "then item")

SELFTESTS = [("selftest_guard_peer_samerow.py", 13, 0),
             ("selftest_guard_peer_jev.py", 17, 0),
             ("selftest_guard_peer_ladder.py", 21, 0),
             ("selftest_guard_bash_jev.py", 11, 0)]

FAILS = []
for _s in (sys.stdout, sys.stderr):        # this console is cp949; a 🔴 in a NEXT bullet would kill the run
    try:
        _s.reconfigure(errors="backslashreplace")
    except Exception:      # noqa: BLE001
        pass


def gate(name, ok, detail=""):
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        FAILS.append(name)
    sys.stdout.flush()
    return ok


def ledger_tokens():
    total = 0
    try:
        with open(jev.LEDGER, encoding="utf-8") as fh:
            for l in fh:
                if not l.strip():
                    continue
                try:
                    u = json.loads(l).get("usage")
                except ValueError:
                    continue
                if isinstance(u, dict):
                    total += u.get("input_tokens") or 0
    except OSError:
        return 0
    return total


def pmap(fn, items, workers=4):
    out = [None] * len(items)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, it): i for i, it in enumerate(items)}
        for f in cf.as_completed(futs):
            i = futs[f]
            try:
                out[i] = f.result()
            except Exception as e:      # noqa: BLE001
                out[i] = ("error", str(e)[:120])
    return out


# ================================================================================== T1  THE FOUR SELF-TESTS
def run_selftests():
    print("\n=== T1 SELF-TESTS ----------------------------------------------------------------------")
    rows = []
    for name, want_pass, want_fail in SELFTESTS:
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, "-u", os.path.join(HERE, name)], cwd=ROOT,
                               capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=420)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except Exception as e:          # noqa: BLE001
            rc, out = 99, "%s: %s" % (type(e).__name__, e)
        m = re.search(r"(\d+)\s*pass(?:es)?\s*/\s*(\d+)\s*fail", out, re.I)
        np_, nf_ = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
        rows.append({"file": name, "rc": rc, "pass": np_, "fail": nf_, "secs": round(time.time() - t0, 1)})
        gate("T1 %s ends rc=0" % name, rc == 0, "rc=%s, %s pass / %s fail, %.0f s" % (
            rc, np_, nf_, time.time() - t0))
        gate("T1b %s at its recorded size" % name, np_ >= want_pass and nf_ == want_fail,
             "got %s/%s, expected >=%d pass / %d fail" % (np_, nf_, want_pass, want_fail))
        if rc != 0 or nf_ not in (0, want_fail):
            # Echo the failing rows with the word disarmed: bgrun's inner-failure scanner would otherwise read
            # a QUOTED failure as this run's own (the carve-out guard_peer.SELFTEST_LOG_RE documents).
            for ln in out.splitlines():
                if re.match(r"^\s*\*{0,2}FAIL\b", ln):
                    print("      (from %s) %s" % (name, ln.strip().replace("FAIL", "F.A.I.L", 1)[:150]))
    return rows


# =========================================================== T2  WHAT THE SAME-ROW RULE WOULD HAVE AVOIDED
def review_stems(body):
    """Every tools/recipes|bench script name a review NAMES where a dispatch names its subject, `_vN`
    stripped. Same two places guard_peer.review_names_script() reads, so the count cannot be kinder than
    the rule."""
    hay = []
    m = guard_peer.QUESTION_SEC_RE.search(body)
    if m:
        hay.append(m.group(1))
    hay.extend(guard_peer.TASK_SLUG_RE.findall(body))
    stems = set()
    for h in hay:
        for nm in guard_peer.SCRIPT_IN_CMD_RE.findall(h):
            stems.add(guard_peer.VSUFFIX_RE.sub("", nm))
    return stems


def born_of(p):
    st = os.stat(p)
    return min(st.st_ctime, st.st_mtime) if os.name == "nt" else st.st_mtime


def trial_samerow():
    print("\n=== T2 ONE REVIEW PER ROW PER CYCLE: what it would have avoided -------------------------")
    reviews = []
    for p in sorted(glob.glob(os.path.join(PEER, "*.md"))):
        try:
            b = born_of(p)
            if not (WIN_FROM <= b < WIN_TO):
                continue
            body = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        ok, why = guard_peer.review_quality(body)
        reviews.append({"path": p, "name": os.path.basename(p), "born": b, "ok": ok, "why": why,
                        "body": body, "stems": review_stems(body)})
    reviews.sort(key=lambda r: r["born"])
    n_ok = sum(1 for r in reviews if r["ok"])
    print("  %d reviews archived 2026-09-21..22 ; %d of them citable (ANSWERED + adversary)" % (
        len(reviews), n_ok))

    logs = []
    import logclass
    for p in glob.glob(os.path.join(HERE, "*.log")):
        base = os.path.basename(p)
        if logclass.is_review_log(p) or guard_peer.SELFTEST_LOG_RE.match(base):
            continue
        try:
            st = os.stat(p)
            if not (WIN_FROM <= st.st_mtime < WIN_TO):
                continue
            text = open(p, encoding="utf-8", errors="replace").read().lstrip("﻿")
        except OSError:
            continue
        last = text.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in text else text
        if not guard_peer.FAILURE_RE.search(last):
            continue
        stem = guard_peer.log_script(last)
        if not stem:
            continue
        logs.append({"name": base, "mtime": st.st_mtime, "stem": stem})
    logs.sort(key=lambda r: r["mtime"])
    print("  %d failing bench logs in the same window carry a readable script name" % len(logs))

    released, avoided = [], {}
    for L in logs:
        prior = [r for r in reviews
                 if r["ok"] and r["born"] <= L["mtime"] <= r["born"] + guard_peer.SAME_ROW_AGE_S
                 and guard_peer.review_names_script(r["body"], L["stem"])]
        if not prior:
            continue
        cite = max(prior, key=lambda r: r["born"])
        released.append({"log": L["name"], "stem": L["stem"], "cited": cite["name"],
                         "age_min": int((L["mtime"] - cite["born"]) / 60)})
        later = [r for r in reviews if r["born"] > L["mtime"]
                 and guard_peer.review_names_script(r["body"], L["stem"])]
        if later:
            nxt = min(later, key=lambda r: r["born"])
            avoided.setdefault(nxt["name"], []).append(L["name"])

    print("  RELEASED WITHOUT A NEW REVIEW: %d failing logs" % len(released))
    for r in released:
        print("    %-44s stem=%-28s <- %s (%d min)" % (r["log"][:44], r["stem"][:28], r["cited"], r["age_min"]))
    print("  REVIEWS THE RULE WOULD HAVE AVOIDED BUYING: %d" % len(avoided))
    for k in sorted(avoided):
        print("    %-58s (charged to: %s)" % (k, ", ".join(avoided[k])[:70]))
    gate("T2 the avoided-review count was computed", True, "%d reviews, %d released logs" % (
        len(avoided), len(released)))
    return {"n_reviews_window": len(reviews), "n_citable": n_ok, "n_failing_logs": len(logs),
            "released": released, "avoided": {k: v for k, v in avoided.items()}}


# ================================================================================== T3-T5  DRIFT, RE-RUN
def next_blocks(windows):
    """{window id: the WHOLE NEXT section} re-extracted from git, so the set cannot drift from the document."""
    acts = {}
    for w in windows:
        try:
            txt = subprocess.run(["git", "show", "%s:STATUS.md" % w["sha"]], cwd=ROOT, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", timeout=60).stdout
        except Exception as e:          # noqa: BLE001
            print("    (git show %s failed: %s)" % (w["sha"], e))
            txt = ""
        acts[w["id"]] = jd.next_block(text=txt) if txt else ""
    return acts


def marker_rows():
    rows = []
    try:
        with open(MARKER, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                if ln.startswith("#") or "\t" not in ln:
                    continue
                p = ln.rstrip("\n").split("\t")
                if len(p) >= 3:
                    rows.append((p[0], p[2]))
    except OSError:
        pass
    return rows


def adjusted_labels(items):
    """The second label set: an item the hand-off ITSELF names is on-task under the new question. Driven by
    ADJUST_PHRASES over each item's own `why`, with `same ...` inheriting from the item above."""
    out, prev = [], False
    for it in items:
        why = (it.get("why") or "").lower()
        flip = any(ph in why for ph in ADJUST_PHRASES)
        if not flip and why.startswith("same ") and prev:
            flip = True
        prev = flip
        out.append("on" if (flip and it["label"] == "off") else it["label"])
    return out


def trial_drift():
    print("\n=== T3-T5 PER-COMMAND DRIFT, against the WHOLE NEXT -------------------------------------")
    doc = json.load(open(DRIFT_SET, encoding="utf-8"))
    acts = next_blocks(doc["windows"])
    for w in doc["windows"]:
        a = acts.get(w["id"], "")
        print("  window %s (%s): NEXT %d chars, %d bullets | %s" % (
            w["id"], w["sha"], len(a), len(a.splitlines()), a.splitlines()[0][:95] if a else "(EMPTY)"))
    gate("T3a all three NEXT sections were recovered from git", all(acts.get(w["id"]) for w in doc["windows"]),
         ", ".join("%s=%d" % (k, len(v)) for k, v in sorted(acts.items())))

    rows_all = marker_rows()
    by_ts = {}
    for i, (ts, cmd) in enumerate(rows_all):
        by_ts.setdefault(ts, (i, cmd))
    adj = adjusted_labels(doc["items"])
    jobs, meta = [], []
    for it, alabel in zip(doc["items"], adj):
        hit = by_ts.get(it["ts"])
        if not hit:
            print("  MISS  %s not in the marker log" % it["ts"])
            continue
        idx, cmd = hit
        recent = [c for _t, c in rows_all[max(0, idx - 5):idx]]
        jobs.append((acts.get(it["window"], ""), cmd, recent))
        meta.append(dict(it, adj=alabel))
    gate("T3b every labelled command was found in the marker log", len(jobs) == len(doc["items"]),
         "%d/%d" % (len(jobs), len(doc["items"])))

    res = pmap(lambda j: jd.judge(j[1], act=j[0], recent=j[2], retries=1, n=SAMPLES,
                                  purpose="drift-trial-wave3a"), jobs)
    rows, answered = [], 0
    for it, (_act, cmd, _r), out in zip(meta, jobs, res):
        if not isinstance(out, tuple) or len(out) != 3 or out[0] is None:
            print("  ERR  %s %s" % (it["ts"], out))
            continue
        p, what, _err = out
        answered += 1
        pred = "off" if p <= jd.DRIFT_LO else "on"
        rows.append({"ts": it["ts"], "window": it["window"], "truth": it["label"], "adj": it["adj"],
                     "p": round(p, 3), "pred": pred, "what": what,
                     "ok": pred == it["label"], "ok_adj": pred == it["adj"],
                     "cmd": cmd[:150], "why": it["why"]})
    gate("T3 every labelled command got a consensus probability back", answered == len(jobs),
         "%d/%d at n=%d" % (answered, len(jobs), SAMPLES))

    n = len(rows)
    if not n:
        return {"n": 0}
    acc = sum(r["ok"] for r in rows) / n
    acc_adj = sum(r["ok_adj"] for r in rows) / n
    brier = sum((r["p"] - (1.0 if r["truth"] == "on" else 0.0)) ** 2 for r in rows) / n
    brier_adj = sum((r["p"] - (1.0 if r["adj"] == "on" else 0.0)) ** 2 for r in rows) / n
    on_o = [r for r in rows if r["truth"] == "on"]
    off_o = [r for r in rows if r["truth"] == "off"]
    on_a = [r for r in rows if r["adj"] == "on"]
    off_a = [r for r in rows if r["adj"] == "off"]
    print("  T4 ORIGINAL LABELS (comparable with the 77.4 %% on record): %d/%d = %.1f %%  Brier %.3f"
          % (sum(r["ok"] for r in rows), n, 100 * acc, brier))
    print("     off-task caught %d/%d ; FALSE ALARMS on on-task %d/%d   (was %s)" % (
        sum(r["ok"] for r in off_o), len(off_o), sum(1 for r in on_o if not r["ok"]), len(on_o),
        OLD_FALSE_ALARMS))
    print("  T4b ADJUSTED LABELS (acts the same hand-off names are on-task): %d/%d = %.1f %%  Brier %.3f"
          % (sum(r["ok_adj"] for r in rows), n, 100 * acc_adj, brier_adj))
    print("      off-task caught %d/%d ; FALSE ALARMS on on-task %d/%d" % (
        sum(r["ok_adj"] for r in off_a), len(off_a), sum(1 for r in on_a if not r["ok_adj"]), len(on_a)))
    print("      relabelled by ADJUST_PHRASES: %d items" % sum(1 for r in rows if r["truth"] != r["adj"]))
    seq = [r for r in rows if "defers" in r["why"] or "past the first" in r["why"] or "THEN item" in r["why"]]
    print("  T5 `sequel` subset (a later act of the SAME hand-off): %d/%d now read ON-TASK   %s" % (
        sum(1 for r in seq if r["pred"] == "on"), len(seq),
        " ".join("p=%.2f" % r["p"] for r in seq)))
    print("  DISAGREEMENTS (against the adjusted labels):")
    for r in rows:
        if not r["ok_adj"]:
            print("    %s [%s] truth=%-3s adj=%-3s p=%.2f what=%-10s %s" % (
                r["ts"], r["window"], r["truth"], r["adj"], r["p"], r["what"], r["cmd"][:80]))
    return {"n": n, "accuracy": acc, "accuracy_adj": acc_adj, "brier": brier, "brier_adj": brier_adj,
            "samples": SAMPLES, "sequel_on": sum(1 for r in seq if r["pred"] == "on"), "sequel_n": len(seq),
            "rows": rows}


def main():
    t0, tok0 = time.time(), ledger_tokens()
    print("=== jev_wave3a_trials  %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=== key present: %s ; consensus n=%d ; budget $%.2f" % (bool(jev.get_key()), SAMPLES, BUDGET_USD))
    out = {}
    for name, fn in (("selftests", run_selftests), ("samerow", trial_samerow), ("drift", trial_drift)):
        try:
            out[name] = fn()
        except Exception as e:      # noqa: BLE001 - one trial's failure must not lose the others
            import traceback
            traceback.print_exc()
            gate("trial %s completed" % name, False, "%s: %s" % (type(e).__name__, str(e)[:120]))
            out[name] = {"error": "%s: %s" % (type(e).__name__, str(e)[:200])}
    dtok = ledger_tokens() - tok0
    usd = dtok / 1e6 * USD_PER_MTOK_IN
    print("\n=== SPEND: %d input tokens this run ~= $%.4f at the measured $%.4f/Mtok" % (
        dtok, usd, USD_PER_MTOK_IN))
    gate("T6 total Jev spend under $%.2f" % BUDGET_USD, usd < BUDGET_USD, "$%.4f" % usd)
    out["spend"] = {"input_tokens": dtok, "usd": usd}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("=== readings -> %s" % OUT)
    print("=== %d FAIL(s): %s ; wall %.0f s" % (len(FAILS), FAILS or "-", time.time() - t0))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
