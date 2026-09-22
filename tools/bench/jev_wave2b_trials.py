r"""jev_wave2b_trials.py - MEASURE second-wave insertions #4, #3, #5 and #7 of docs/jev-integration-plan.md,
in one run, one log, one notification (CLAUDE.md section 3, "one LabVIEW batch = one runner").

PREDICTION CONTRACT (written before the run):
  W1  #4 DRIFT     every labelled command gets a probability back              -> 31/31, REPORTED
  W2  #4           accuracy at the decision threshold p <= 0.30 = off-task     -> REPORTED, not gated
  W3  #4           the `sequel` subset (a later act of the SAME hand-off) is broken out separately
  W4  #3 PREFLIGHT every natural item gets a class back                        -> 15/15, REPORTED
  W5  #3           accuracy over the 15 natural items; the 3 synthetic wrong-input controls reported apart
  W6  #5 ROWCHECK  20 true rows + 20 corrupted rows, accuracy and the corruption that survives -> REPORTED
  W7  #7 CONTRADICT<=600 pairs x 3 samples, plus 12 known supersession pairs as positive controls -> REPORTED
  W8  total Jev spend for the run stays under $0.20                            -> GATED (the user's budget)
  ⚠️ NOTHING HERE TOUCHES LabVIEW, COM, a .vi, or a motor. It reads files, calls tools/jev.py, and prints.

PRIOR ART CHECKED before writing (CLAUDE.md, "check what already exists"):
  tools/bench/jev_trial.py / jev_next_trial.py / jev_discharge_trial.py / jev_priorart_trial.py /
  jev_triage_trial.py  - the first-wave trials; this file copies their shape (set file -> loop -> accuracy,
                         Brier, disagreement list -> JSON readings) and re-implements none of their logic.
  tools/jev.py         - transport, ledger, unknown band.
  tools/jev_drift.py, tools/jev_preflight.py, tools/jev_rowcheck.py, tools/jev_contradict.py - the four
                         modules under test. The questions live THERE, not here: a trial that asks its own
                         question measures something the gate will never ask.
"""
import concurrent.futures as cf
import json
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import jev                      # noqa: E402
import jev_contradict as jc     # noqa: E402
import jev_drift as jd          # noqa: E402
import jev_preflight as jp      # noqa: E402
import jev_rowcheck as jr       # noqa: E402

DRIFT_SET = os.path.join(HERE, "jev_drift_set.json")
PRE_SET = os.path.join(HERE, "jev_preflight_set.json")
OUT = os.path.join(HERE, "jev_wave2b_trials.json")
MARKER = os.path.join(ROOT, "tools", "hooks", "material_marker.log")
SCRATCH = os.path.join(HERE, "_wave2b_scratch")
BUDGET_USD = 0.20
USD_PER_MTOK_IN = 0.0427        # measured: 585,940 input tokens over the first 326 calls cost $0.025

FAILS = []
random.seed(20260922)

# This console is cp949: a STATUS bullet's 🔴 or a plan item's ⚠️ would raise UnicodeEncodeError mid-run and
# throw away the measurement (it did, on the first self-test). Escape what the codec cannot carry.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="backslashreplace")
    except Exception:      # noqa: BLE001 - older streams have no reconfigure; the try/except IS the fallback
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
                    u = json.loads(l).get("usage")      # a failed call logs usage: null
                except ValueError:
                    continue
                if isinstance(u, dict):
                    total += u.get("input_tokens") or 0
    except OSError:
        return 0
    return total


def pmap(fn, items, workers=4):
    """Ordered parallel map. Jev calls are network-bound; four at a time keeps the wall clock sane without
    provoking the 429s that jev.ask would then have to back off from."""
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


# ============================================================================================ #4  DRIFT
def next_first_acts(windows):
    """{window id: first act text} re-extracted from git, so the set cannot drift from the document."""
    acts = {}
    for w in windows:
        try:
            txt = subprocess.run(["git", "show", "%s:STATUS.md" % w["sha"]], cwd=ROOT, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", timeout=60).stdout
        except Exception as e:          # noqa: BLE001
            print("    (git show %s failed: %s)" % (w["sha"], e))
            txt = ""
        acts[w["id"]] = jd.first_act(text=txt) if txt else ""
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


def trial_drift():
    print("\n=== #4 PER-COMMAND DRIFT ---------------------------------------------------------------")
    doc = json.load(open(DRIFT_SET, encoding="utf-8"))
    acts = next_first_acts(doc["windows"])
    for w in doc["windows"]:
        print("  window %s (%s): first act %d chars | %s" % (
            w["id"], w["sha"], len(acts.get(w["id"], "")), acts.get(w["id"], "")[:110]))
    rows_all = marker_rows()
    by_ts = {}
    for i, (ts, cmd) in enumerate(rows_all):
        by_ts.setdefault(ts, (i, cmd))
    jobs, meta = [], []
    for it in doc["items"]:
        hit = by_ts.get(it["ts"])
        if not hit:
            print("  MISS  %s not in the marker log" % it["ts"])
            continue
        idx, cmd = hit
        recent = [c for _t, c in rows_all[max(0, idx - 5):idx]]
        jobs.append((acts.get(it["window"], ""), cmd, recent))
        meta.append(it)
    gate("W1a every labelled command was found in the marker log",
         len(jobs) == len(doc["items"]), "%d/%d" % (len(jobs), len(doc["items"])))

    res = pmap(lambda j: jd.judge(j[1], act=j[0], recent=j[2], retries=1, purpose="drift-trial"), jobs)
    rows, answered = [], 0
    for it, (act, cmd, _r), out in zip(meta, jobs, res):
        if not isinstance(out, tuple) or len(out) != 3 or out[0] is None:
            print("  ERR  %s %s" % (it["ts"], out))
            continue
        p, what, _err = out
        answered += 1
        pred = "off" if p <= jd.DRIFT_LO else "on"
        rows.append({"ts": it["ts"], "window": it["window"], "truth": it["label"], "p": p, "pred": pred,
                     "what": what, "ok": pred == it["label"], "cmd": cmd[:150], "why": it["why"]})
    gate("W1 every labelled command got a probability back", answered == len(jobs),
         "%d/%d" % (answered, len(jobs)))
    n = len(rows)
    acc = sum(r["ok"] for r in rows) / n if n else 0
    brier = sum((r["p"] - (1.0 if r["truth"] == "on" else 0.0)) ** 2 for r in rows) / n if n else 0
    off = [r for r in rows if r["truth"] == "off"]
    on = [r for r in rows if r["truth"] == "on"]
    print("  W2 ACCURACY (p<=0.30 => off-task): %d/%d = %.1f %%  Brier %.3f" % (
        sum(r["ok"] for r in rows), n, 100 * acc, brier))
    print("     off-task caught %d/%d ; FALSE ALARMS on on-task %d/%d" % (
        sum(r["ok"] for r in off), len(off), sum(1 for r in on if not r["ok"]), len(on)))
    print("     p range: on-task %.2f..%.2f ; off-task %.2f..%.2f" % (
        min([r["p"] for r in on] or [0]), max([r["p"] for r in on] or [0]),
        min([r["p"] for r in off] or [0]), max([r["p"] for r in off] or [0])))
    seq = [r for r in rows if "defers" in r["why"] or "past the first" in r["why"] or "THEN item" in r["why"]]
    print("  W3 `sequel` subset (a later act of the SAME hand-off, labelled off): %d/%d read as off-task" % (
        sum(r["ok"] for r in seq), len(seq)))
    print("  DISAGREEMENTS:")
    for r in rows:
        if not r["ok"]:
            print("    %s [%s] truth=%-3s p=%.2f what=%-10s %s" % (
                r["ts"], r["window"], r["truth"], r["p"], r["what"], r["cmd"][:88]))
    return {"n": n, "accuracy": acc, "brier": brier, "rows": rows}


# ========================================================================================= #3  PRE-FLIGHT
def trial_preflight():
    print("\n=== #3 PRE-FLIGHT ----------------------------------------------------------------------")
    doc = json.load(open(PRE_SET, encoding="utf-8"))
    items = [dict(it, abspath=os.path.join(ROOT, it["path"])) for it in doc["items"]]
    missing = [it["path"] for it in items if not os.path.exists(it["abspath"])]
    gate("W4a every labelled script exists", not missing, str(missing[:3]))
    items = [it for it in items if os.path.exists(it["abspath"])]

    sc = doc["synthetic_controls"]
    os.makedirs(SCRATCH, exist_ok=True)
    controls = []
    for src in sc["from"]:
        s = os.path.join(ROOT, src)
        if not os.path.exists(s):
            continue
        txt = open(s, encoding="utf-8", errors="replace").read()
        sub, nrep = re.subn(r"D1_s3b_[\w.]+\.vi", sc["stale_vi"], txt)
        if not nrep:
            print("  (no VI literal to stale in %s - control skipped)" % src)
            continue
        dst = os.path.join(SCRATCH, "CTL_" + os.path.basename(src))
        open(dst, "w", encoding="utf-8").write(sub)
        controls.append({"path": os.path.relpath(dst, ROOT), "abspath": dst, "label": sc["label"],
                         "evidence": "synthetic: %s -> %s (%d substitutions)" % (src, sc["stale_vi"], nrep)})

    res = pmap(lambda it: jp.classify(it["abspath"], retries=1, purpose="preflight-trial"),
               items + controls, workers=3)
    rows, ctl_rows = [], []
    for it, out in zip(items + controls, res):
        if not isinstance(out, tuple) or len(out) != 5:
            print("  ERR  %s %s" % (it["path"], out))
            continue
        cls, p, findings, static, err = out
        rec = {"path": it["path"], "truth": it["label"], "cls": cls, "p": p, "ok": cls == it["label"],
               "err": err, "lines": static.get("lines"), "stagekit": static.get("stagekit"),
               "n_unmeasured": static.get("n_unmeasured"), "save_route": static.get("save_route"),
               "pct_mismatch": static.get("pct_mismatch"), "findings": findings}
        (ctl_rows if it in controls else rows).append(rec)
        print("  %-4s %-46s truth=%-13s -> %-13s p=%s  [%d ln, kit=%s, unmeasured=%s, save=%s, %%=%s]" % (
            "OK" if rec["ok"] else "DIFF", os.path.basename(it["path"])[:46], it["label"], cls,
            ("%.2f" % p) if p is not None else "?", static.get("lines") or -1, static.get("stagekit"),
            static.get("n_unmeasured"), static.get("save_route"), static.get("pct_mismatch")))
    gate("W4 every natural item got a class back", all(r["cls"] for r in rows),
         "%d/%d" % (sum(1 for r in rows if r["cls"]), len(rows)))
    n = len(rows)
    acc = sum(r["ok"] for r in rows) / n if n else 0
    print("  W5 ACCURACY over the %d natural items: %d/%d = %.1f %%" % (
        n, sum(r["ok"] for r in rows), n, 100 * acc))
    print("     synthetic wrong-input controls: %d/%d classed wrong-input  (%s)" % (
        sum(r["ok"] for r in ctl_rows), len(ctl_rows), ", ".join(str(r["cls"]) for r in ctl_rows)))
    byclass = {}
    for r in rows:
        byclass.setdefault(r["truth"], []).append(r["ok"])
    for k, v in sorted(byclass.items()):
        print("     %-14s %d/%d" % (k, sum(v), len(v)))
    return {"n": n, "accuracy": acc, "rows": rows, "controls": ctl_rows}


# ========================================================================================== #5  ROW TABLE
def corrupt(row, by_uid, rng):
    """One deliberately wrong row + the name of the corruption. Never returns the row unchanged."""
    r = json.loads(json.dumps(row))
    src = r.get("source") or {}
    kinds = ["swap-uids", "wrong-sink-name", "wrong-source-name", "wrong-index", "flip-direction",
             "alien-uid"]
    k = rng.choice(kinds)
    if k == "swap-uids":
        src["uid"], r["uid"] = r.get("uid"), src.get("uid")
    elif k == "wrong-sink-name":
        r["name"] = "Total Lost Frames" if r.get("name") != "Total Lost Frames" else "error out"
    elif k == "wrong-source-name":
        src["name"] = "Z reference" if src.get("name") != "Z reference" else "error in (no error)"
    elif k == "wrong-index":
        r["i"] = (r.get("i") or 0) + 7
    elif k == "flip-direction":
        r["is_source"] = not bool(r.get("is_source"))
        src["is_source"] = not bool(src.get("is_source"))
    else:
        r["uid"] = 999001
    r["source"] = src
    return r, k


def trial_rowcheck(n_pos=20, n_neg=20):
    print("\n=== #5 ROW-TABLE CHECK -----------------------------------------------------------------")
    rows_tbl, by_uid = jr.load_tables()
    gate("W6a the measured tables loaded", bool(rows_tbl) and bool(by_uid),
         "%d rows, %d uids indexed" % (len(rows_tbl), len(by_uid)))
    usable = [r for r in rows_tbl if (r.get("source") or {}).get("uid") is not None]
    rng = random.Random(20260922)
    pos = rng.sample(usable, min(n_pos, len(usable)))
    neg_src = rng.sample(usable, min(n_neg, len(usable)))
    negs = [corrupt(r, by_uid, rng) for r in neg_src]
    jobs = [(r, "true") for r in pos] + [(r, "corrupt", k) for r, k in negs]
    res = pmap(lambda j: jr.check_row(j[0], by_uid, retries=1, purpose="rowcheck-trial"), jobs, workers=4)
    rows = []
    for j, out in zip(jobs, res):
        if not isinstance(out, tuple) or len(out) != 3:
            continue
        p, verdict, err = out
        truth = "ok" if j[1] == "true" else "suspect"
        rows.append({"truth": truth, "verdict": verdict, "p": p, "how": (j[2] if len(j) > 2 else "-"),
                     "ok": verdict == truth, "err": err,
                     "row": jr.row_text(j[0])[:150]})
    pos_rows = [r for r in rows if r["truth"] == "ok"]
    neg_rows = [r for r in rows if r["truth"] == "suspect"]
    n = len(rows)
    acc = sum(r["ok"] for r in rows) / n if n else 0
    print("  W6 ACCURACY %d/%d = %.1f %% ; true rows %d/%d ok ; corrupted %d/%d flagged" % (
        sum(r["ok"] for r in rows), n, 100 * acc,
        sum(r["ok"] for r in pos_rows), len(pos_rows), sum(r["ok"] for r in neg_rows), len(neg_rows)))
    bykind = {}
    for r in neg_rows:
        bykind.setdefault(r["how"], []).append(r["ok"])
    for k, v in sorted(bykind.items()):
        print("     corruption %-18s caught %d/%d" % (k, sum(v), len(v)))
    print("  SURVIVING CORRUPTIONS (read as consistent):")
    for r in neg_rows:
        if not r["ok"]:
            print("    %-18s p=%s %s" % (r["how"], ("%.2f" % r["p"]) if r["p"] is not None else "?", r["row"][:96]))
    print("  FALSE ALARMS on true rows:")
    for r in pos_rows:
        if not r["ok"]:
            print("    p=%s %s" % (("%.2f" % r["p"]) if r["p"] is not None else "?", r["row"][:110]))
    return {"n": n, "accuracy": acc, "rows": rows}


# ===================================================================================== #7  CONTRADICTIONS
CONTROLS = [("33", "32"), ("38", "37"), ("40", "36"), ("66", "61"), ("70", "66"), ("84", "78"),
            ("87", "80"), ("88", "81"), ("89", "82"), ("90", "79"), ("109", "107"), ("120", "117"),
            ("126", "121")]


def trial_contradict(cap=600, samples=3, top=15):
    print("\n=== #7 PRE-DECIDED CONTRADICTIONS ------------------------------------------------------")
    items = jc.parse_items()
    gate("W7a the plan parsed into numbered items", len(items) > 100, "%d items" % len(items))
    byid = {it["id"]: it for it in items}
    pairs = jc.build_pairs(items, cap=cap)
    print("  %d pairs (<=8 earlier items each, >=2 shared uncommon tokens, cap %d), %d samples each" % (
        len(pairs), cap, samples))
    have = {(items[i]["id"], items[j]["id"]) for _s, i, j in pairs}
    ctl_present = [c for c in CONTROLS if c in have]
    print("  control pairs that the OVERLAP HEURISTIC would have surfaced on its own: %d/%d %s" % (
        len(ctl_present), len(CONTROLS), ctl_present))

    jobs = [(items[i]["id"], items[j]["id"], items[i]["text"], items[j]["text"], s) for s, i, j in pairs]
    ctl_jobs = [(a, b, byid[a]["text"], byid[b]["text"], -1) for a, b in CONTROLS if a in byid and b in byid]
    t0 = time.time()
    res = pmap(lambda j: jc.ask_pair(j[2], j[3], samples=samples, retries=1, purpose="contradict-trial"),
               jobs + ctl_jobs, workers=4)
    rows, ctls = [], []
    for j, out in zip(jobs + ctl_jobs, res):
        if not isinstance(out, tuple) or len(out) != 3 or out[0] is None:
            continue
        p, ps, _err = out
        rec = {"a": j[0], "b": j[1], "p": p, "spread": (max(ps) - min(ps)) if ps else 0.0, "shared": j[4],
               "a_title": byid[j[0]]["title"][:110], "b_title": byid[j[1]]["title"][:110]}
        (ctls if j[4] == -1 else rows).append(rec)
    rows.sort(key=lambda r: -r["p"])
    hits = [r for r in rows if r["p"] >= 0.80]
    print("  answered %d/%d pairs in %.0f s ; %d at p >= 0.80" % (
        len(rows), len(jobs), time.time() - t0, len(hits)))
    ctl_hit = sum(1 for r in ctls if r["p"] >= 0.80)
    print("  W7 CONTROL HIT RATE (known WITHDRAWN/SUPERSEDED/AMENDED pairs at p >= 0.80): %d/%d" % (
        ctl_hit, len(ctls)))
    for r in sorted(ctls, key=lambda r: -r["p"]):
        print("     %5.2f  %-5s supersedes %-5s | %s" % (r["p"], r["a"], r["b"], r["a_title"][:78]))
    print("  TOP %d SUSPECTS (mean of %d samples):" % (top, samples))
    for r in rows[:top]:
        print("    %5.2f (+-%.2f) %-5s vs %-5s shared=%-3d | %s || %s" % (
            r["p"], r["spread"] / 2, r["a"], r["b"], r["shared"], r["a_title"][:62], r["b_title"][:62]))
    return {"n_pairs": len(rows), "n_hits": len(hits), "controls": ctls, "control_hits": ctl_hit,
            "rows": rows[:60]}


def main():
    t0, tok0 = time.time(), ledger_tokens()
    print("=== jev_wave2b_trials  %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=== key present: %s" % bool(jev.get_key()))
    out = {}
    for name, fn in (("drift", trial_drift), ("preflight", trial_preflight),
                     ("rowcheck", trial_rowcheck), ("contradict", trial_contradict)):
        try:
            out[name] = fn()
        except Exception as e:      # noqa: BLE001 - one trial's failure must not lose the other three
            import traceback
            traceback.print_exc()
            gate("trial %s completed" % name, False, "%s: %s" % (type(e).__name__, str(e)[:120]))
            out[name] = {"error": "%s: %s" % (type(e).__name__, str(e)[:200])}
    dtok = ledger_tokens() - tok0
    usd = dtok / 1e6 * USD_PER_MTOK_IN
    print("\n=== SPEND: %d input tokens this run ~= $%.4f at the measured $%.4f/Mtok" % (
        dtok, usd, USD_PER_MTOK_IN))
    gate("W8 total Jev spend under $%.2f" % BUDGET_USD, usd < BUDGET_USD, "$%.4f" % usd)
    out["spend"] = {"input_tokens": dtok, "usd": usd}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("=== readings -> %s" % OUT)
    print("=== %d FAIL(s): %s ; wall %.0f s" % (len(FAILS), FAILS or "-", time.time() - t0))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
