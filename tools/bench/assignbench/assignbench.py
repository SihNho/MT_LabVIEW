r"""assignbench - bench for a CYCLE ASSIGNMENT AGENT on known-answer decision points from cycles 130-143 (card chat-B6).

    py tools/bgrun.py --material --max-min N --log tools/bench/assignbench/<x>.log -- py -u tools/bench/assignbench/assignbench.py
        --lock                                 worktree per case at its base commit, copies in, leak-check, pin rubric md5s
        --stub hit|miss|ratelimit [--reps 1]   dry run: claude replaced by decbench/stub_dec.py (no model calls)
        --reps 2 [--par 6] [--guard-usd 150]   full run (real cells; cloud only per the card)

PREDICTION CONTRACT: cases from make_cases.py (21: RETRY 5, ISSUE 6, HANDBACK 6, CLOSE 3, ESCALATE 1). Arms OM / OH / SM /
SH = claude-opus-5-5 medium / high (OH = today's judgement agent, the baseline) and claude-sonnet-5-5 medium / high.
Every arm-run is decbench.run_arm (one read-only cell in the case worktree, dec_guard hook, rate-limit re-queue <= 3,
cap --cap-min), scored by dec_score: mechanical (M1 = the ACTION line matches the known action, M2 = the card/question
content, F1 = a forbidden action, B1 bonus) and ONE blind Opus-high scorer cell per case (decbench.blind). USD and
minutes per arm-run come from the cell envelope. Stub run: hit -> every arm M1 = 1 on every case, no model call, no
LabVIEW pid, no worktree left. Ends with a RESULT line.

WHAT EXISTED FIRST: decbench (prepare / leak_check / run_cell / run_arm / blind, stub_dec.py) and dec_score (mechanical,
combine, blind_prompt, parse_blind, aggregate) - imported, not copied; decbench.py gained the Linux port of the Sonnet
cloud bench (sonnet-bench-20261002 fb1cb94f) and stub_dec.py a DECBENCH_CASES / stub_answer hook. New here: the case set,
the arms, the assignment prompt, the action confusion table and the per-case cost table.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DECB = os.path.join(os.path.dirname(HERE), "decbench")
sys.path.insert(0, DECB)
import decbench as DB  # noqa: E402  (sets TEMP on POSIX, imports matbench + dec_score)
import dec_score as DS  # noqa: E402

MB = DB.MB
CASES_P = os.path.join(HERE, "cases.json")
LOCK_P = os.path.join(HERE, "cases_lock.json")
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
ARMS = {"OM": (OPUS, "medium"), "OH": (OPUS, "high"), "SM": (SONNET, "medium"), "SH": (SONNET, "high")}
DB.ARMS.update(ARMS)                       # run_arm reads DB.ARMS[arm]
os.environ["DECBENCH_CASES"] = CASES_P     # stub_dec.py answers from this bench's cases
ACT_RE = re.compile(r"ACTION:\s*\**\s*([A-Z]+)(\s*\+\s*([A-Z]+))?")


def load():
    d = json.load(open(CASES_P, encoding="utf-8"))
    return d, {c["id"]: c for c in d["cases"]}


def first_action(ans):
    m = ACT_RE.search(ans or "")
    return (m.group(1) + ("+" + m.group(3) if m.group(3) else "")) if m else "NONE"


def do_lock(cases, ids, par):
    try:
        lock = json.load(open(LOCK_P, encoding="utf-8"))
    except (OSError, ValueError):
        lock = {"schema": "assignbench-lock/1", "cases": {}}
    lock["made"] = time.strftime("%Y-%m-%d %H:%M:%S")
    lock["cases"] = {k: v for k, v in lock["cases"].items() if k in cases}

    def one(cid):
        # Same content as decbench.prepare + leak_check (base tree + copied files), read straight from git: decbench's
        # worktree walk took ~10 min per case on this repo (lock.log, first attempt stopped at 4/21).
        c = cases[cid]
        hits, copied = [], []
        if c.get("leak"):
            args = ["grep", "-P", "-I", "-o"] + sum([["-e", p] for p in c["leak"]], []) + [c["base"], "--", "."]
            r = subprocess.run(["git", "-c", "core.longpaths=true"] + args, cwd=MB.MAIN, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            if r.returncode not in (0, 1):     # 1 = no match; anything else (e.g. no PCRE) must not pass as clean
                raise RuntimeError("git grep rc %d: %s" % (r.returncode, r.stderr[:300]))
            out = r.stdout
            hits += ["%s: %r" % (ln.split(":", 2)[1], ln.split(":", 2)[2][:60]) for ln in out.splitlines()
                     if ln.count(":") >= 2]
        pats = [re.compile(p, re.I) for p in c.get("leak", [])]
        for cp in c.get("copy", []):
            data = MB.git_bytes(cp["from"], cp["path"])
            if data is None:
                raise RuntimeError("copy %s:%s missing" % (cp["from"], cp["path"]))
            copied.append({"path": cp["path"], "from": cp["from"], "md5": hashlib.md5(data).hexdigest()})
            txt = data.decode("utf-8", "replace")
            hits += ["%s: %r" % (cp["path"], m.group(0)[:60]) for rx in pats for m in [rx.search(txt)] if m]
        hits += ["ABSENT-VIOLATED " + p for p in c.get("absent", []) if MB.git_bytes(c["base"], p) is not None]
        DB.say("LOCK %s base %s rubric %s leak %s %s" % (cid, c["base"][:8], DB.rubric_md5(c)[:8],
                                                         "PASS" if not hits else "LEAKED", hits[:3]))
        return cid, {"base": c["base"], "rubric_md5": DB.rubric_md5(c), "copied": copied,
                     "leak": "PASS" if not hits else "LEAKED", "leak_hits": hits}
    with cf.ThreadPoolExecutor(par) as ex:
        for cid, rec in ex.map(one, ids):
            lock["cases"][cid] = rec
    json.dump(lock, open(LOCK_P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return [cid for cid in ids if lock["cases"][cid]["leak"] != "PASS"]


def report(path, tag, recs, cases, per_arm, dis, header, arms):
    by = {}
    for r in recs:
        if not r.get("invalid"):
            r["action"] = first_action(r.get("answer"))
            by.setdefault((r["case"], r["arm"]), []).append(r)
    L = ["# assignbench report - %s" % tag, "", header, "",
         "Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0 (dec_score). M1 = the ACTION line "
         "matches the known action (mechanical). blind = one Opus 5.5 high scorer cell per case. usd / min per arm-run.",
         "", "## Per arm", "", "| arm | model / effort | n | invalid | action match (M1 mech) | forbidden hit (mech) | "
         "blind mean | mech mean | usd / run | usd total | min / run |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        rs = [r for r in recs if r["arm"] == arm and not r.get("invalid")]
        a = per_arm.get(arm, {})
        m1 = [r["mech"].get("M1", 0) for r in rs]
        f1 = [r["mech"].get("F1", 0) for r in rs]
        L.append("| %s | %s / %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            arm, ARMS[arm][0], ARMS[arm][1], len(rs), a.get("invalid", 0),
            "%.2f" % (sum(m1) / len(m1)) if m1 else "-", "%.2f" % (sum(f1) / len(f1)) if f1 else "-",
            a.get("blind_mean"), a.get("mech_mean"), a.get("usd_per_run"), a.get("usd_total"), a.get("minutes_mean")))
    L += ["", "## Action match by known action class (M1 mech, all reps)", "",
          "| known action | cases | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for k in sorted({c["known_action"] for c in cases.values()}):
        cids = [c for c in cases if cases[c]["known_action"] == k]
        row = []
        for arm in arms:
            m = [r["mech"].get("M1", 0) for cid in cids for r in by.get((cid, arm), [])]
            row.append("%.2f (%d)" % (sum(m) / len(m), len(m)) if m else "-")
        L.append("| %s | %d | %s |" % (k, len(cids), " | ".join(row)))
    L += ["", "## Per case x arm (answered ACTION per rep ; blind score per rep ; usd mean ; min mean)", "",
          "| case | known | " + " | ".join(arms) + " |", "|---|---|" + "---|" * len(arms)]
    for cid in cases:
        cells = []
        for arm in arms:
            rs = sorted(by.get((cid, arm), []), key=lambda x: x["rep"])
            if not rs:
                cells.append("-")
                continue
            bl = []
            for r in rs:
                b = DS.combine(r.get("blind") or {}, cases[cid]["rubric"])
                bl.append("%.2f" % b["score"] if b and r.get("blind") else "?")
            cells.append("%s ; %s ; $%.2f ; %.1f" % ("/".join(r["action"] for r in rs), "/".join(bl),
                                                    sum(r.get("usd") or 0 for r in rs) / len(rs),
                                                    sum(r.get("minutes") or 0 for r in rs) / len(rs)))
        L.append("| %s | %s | %s |" % (cid, cases[cid]["known_action"], " | ".join(cells)))
    L += ["", "## Mechanical vs blind disagreements (|diff| >= 0.5)", ""] + ["- " + x for x in dis or ["none"]]
    L += ["", "## Known answers (with evidence)", ""] + ["- **%s** (%s): %s" % (cid, c["known_action"], c["known_answer"])
                                                          for cid, c in cases.items()]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="")
    ap.add_argument("--arms", default="OM,OH,SM,SH")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--par", type=int, default=6)
    ap.add_argument("--cap-min", type=float, default=20.0)
    ap.add_argument("--stub", default="")
    ap.add_argument("--lock", action="store_true")
    ap.add_argument("--no-blind", action="store_true")
    ap.add_argument("--guard-usd", type=float, default=150.0)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    DB.SEM = threading.Semaphore(a.par)
    doc, cases = load()
    ids = [x for x in a.cases.split(",") if x] or list(cases)
    arms = [x for x in a.arms.split(",") if x]
    os.makedirs(DB.WTROOT, exist_ok=True)
    lv0, fails, gates = MB.labview_pids(), [], 0
    if a.lock:
        leaked = do_lock(cases, ids, min(a.par, 4))
        gates, fails, art = len(ids), ["%s leaked" % c for c in leaked], LOCK_P
    else:
        lock = json.load(open(LOCK_P, encoding="utf-8"))["cases"]
        bad = [c for c in ids if lock.get(c, {}).get("rubric_md5") != DB.rubric_md5(cases[c]) or lock[c]["leak"] != "PASS"]
        if bad:
            DB.say("REFUSED: rubric md5 changed or leak not PASS: %s" % bad)
            print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
                                          "first_fail": "unlocked cases %s" % bad, "artefacts": []}), flush=True)
            return 1
        runs = os.path.join(HERE, "runs", a.tag)
        os.makedirs(runs, exist_ok=True)
        jobs = [(cid, arm, r) for cid in ids for arm in arms for r in range(1, a.reps + 1)]
        left = {cid: sum(1 for j in jobs if j[0] == cid) for cid in ids}
        wts, spent, wlock = {}, [0.0], threading.Lock()

        def job(cid, arm, rep):
            with wlock:
                if cid not in wts:
                    wts[cid] = DB.prepare(cases[cid])[0]
                wt = wts[cid]
            if spent[0] > a.guard_usd:
                DB.say("COST GUARD %.2f > %.2f: skip %s %s r%d" % (spent[0], a.guard_usd, cid, arm, rep))
                rec = {"case": cid, "arm": arm, "rep": rep, "invalid": True, "skipped": True, "usd": 0.0}
            else:
                rec = DB.run_arm(doc, cases[cid], wt, arm, rep, runs, a.stub, a.cap_min)
            with wlock:
                spent[0] += rec.get("usd") or 0.0
                left[cid] -= 1
                if left[cid] == 0:
                    DB.remove_wt(wts.pop(cid))
            return rec
        with cf.ThreadPoolExecutor(a.par) as ex:
            recs = [f.result() for f in [ex.submit(job, *j) for j in jobs]]
        blind_usd = 0.0
        if not a.no_blind:
            with cf.ThreadPoolExecutor(max(1, min(a.par, len(ids)))) as ex:
                bfs = [ex.submit(DB.blind, doc, cases[cid], [r for r in recs if r["case"] == cid], runs, a.stub,
                                 a.cap_min) for cid in ids]
                blind_usd = sum((f.result() or 0) for f in bfs)
        sub = {c: cases[c] for c in ids}
        per_arm = DS.aggregate(recs, sub)
        dis = DS.disagreements(recs)
        hdr = "tag %s, par %d, reps %d, stub %s, cases %d, arms %s, spent $%.2f (blind $%.2f)" % (
            a.tag, a.par, a.reps, a.stub or "no", len(ids), ",".join(arms), spent[0] + blind_usd, blind_usd)
        report(os.path.join(HERE, "report_%s.md" % a.tag), a.tag, recs, sub, per_arm, dis, hdr, arms)
        res = {"schema": "assignbench-results/1", "tag": a.tag, "stub": a.stub or None, "cases": ids, "arms": arms,
               "per_arm": per_arm, "blind_usd": round(blind_usd, 3), "spent_usd": round(spent[0] + blind_usd, 3),
               "disagreements": dis, "records": recs}
        art = os.path.join(HERE, "results_%s.json" % a.tag)
        json.dump(res, open(art, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        gates = len(recs)
        fails += ["%s %s r%s invalid" % (r["case"], r["arm"], r["rep"]) for r in recs if r.get("invalid")]
        if a.stub == "hit":                    # the harness proof: every stub answer must score as its known action
            fails += ["%s %s r%s M1=%s F1=%s" % (r["case"], r["arm"], r["rep"], r["mech"].get("M1"), r["mech"].get("F1"))
                      for r in recs if not r.get("invalid") and (r["mech"].get("M1") != 1 or r["mech"].get("F1"))]
            fails += ["%s %s r%s no blind score" % (r["case"], r["arm"], r["rep"]) for r in recs
                      if not a.no_blind and not r.get("invalid") and not r.get("blind")]
    leftwt = [w for w in MB.git("worktree", "list").splitlines()
              if DB.WTROOT.replace("\\", "/").lower() in w.replace("\\", "/").lower()]
    new = sorted(set(MB.labview_pids()) - set(lv0))
    fails += (["new LabVIEW pid %s" % new] if new else []) + (["worktrees left %s" % leftwt] if leftwt else [])
    DB.say("WORKTREES LEFT %d; LABVIEW NEW %s" % (len(leftwt), new))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                                  "gates": {"pass": gates - len(fails), "fail": len(fails)},
                                  "first_fail": fails[0] if fails else None,
                                  "artefacts": [{"path": os.path.relpath(art, MB.MAIN).replace("\\", "/"),
                                                 "md5": hashlib.md5(open(art, "rb").read()).hexdigest()}]}), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
