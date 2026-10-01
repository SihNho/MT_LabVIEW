"""run_g2.py - card chat-G5 (Part B of brief_chat-G2.md): 3 arms x 2 repeats over cases_g2.json, blind score, report.

Prior art checked: tools/bench/gsearch/run_arm.py + score.py + report.py (card chat-G1) - same peer.ps1 calls, same
blind-scorer template. This file reuses their logic in ONE runner (answer -> score in the same worker thread, then the
report) so the whole bench is one bgrun, and changes only: the case file (cases_g2.json), the arms, the gemini timeout,
the output dirs (answers_g2/, scores_g2/) and the slugs (g5-*). No peer.ps1 edit.

Arms (same question text + same suffix as G1):
  gemini-pro   peer.ps1 -Agent gemini -Kind fact -Model gemini-3.1-pro-high -TimeoutSec 600   (driver timeout 720 s)
  opus-medium  peer.ps1 -Kind fact                     (role fact as-is: claude-opus-5-5, effort medium, thin, web)
  opus-high    peer.ps1 -Kind fact -Effort high        (peer.ps1's own -Effort override of the same role: identical
               --safe-mode / plan mode / WebSearch+WebFetch allow list; DryRun 2026-09-30 printed exactly that)
               claude arms -TimeoutSec 300 (driver 420 s)
Scorer: peer.ps1 -Agent claude -Kind fact -Model sonnet -Effort low (thin), sees question + known answer + ONE answer
under a random label; never arm/rep/model.
All 6 arm-rep workers run in parallel (as in G1, where all arms ran at once); each is sequential over the cases.

PREDICTION CONTRACT: 8 cases x 3 arms x 2 reps = 48 answer files and 48 score files; every claude answer ANSWERED;
every score line has a grade in {correct, partly, wrong}. Gates: pass = answered+scored cell, fail = non-answer or
unscored. report_g2.md written.
"""
import concurrent.futures as cf, hashlib, json, os, re, subprocess, sys, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PEER = os.path.join(ROOT, "tools", "peer.ps1")
SUFFIX = "\n\nSearch the web and cite the URL of every source you used."
CASES = json.load(open(os.path.join(HERE, "cases_g2.json"), encoding="utf-8"))["cases"]
ARMS = {"gemini-pro": (["-Agent", "gemini", "-Model", "gemini-3.1-pro-high"], 600, 720),
        "opus-medium": ([], 300, 420),
        "opus-high": (["-Effort", "high"], 300, 420)}
PRIMARY = {"LabVIEW VI Scripting": ["ni.com"], "LabVIEW VI Server": ["ni.com"], "NI-IMAQdx": ["ni.com"],
           "LabVIEW ActiveX/COM": ["ni.com"], "NI-VISA": ["ni.com"]}
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'`|,]+")
AD, SD = os.path.join(HERE, "answers_g2"), os.path.join(HERE, "scores_g2")
LOCK = threading.Lock()

TEMPLATE = open(os.path.join(HERE, "score.py"), encoding="utf-8").read().split('TEMPLATE = """', 1)[1].split('"""', 1)[0]


def ps(args, timeout):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PEER] + args
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=timeout)
        return p.stdout.decode("utf-8", "replace"), p.returncode
    except subprocess.TimeoutExpired:
        return "(driver timeout %d s)" % timeout, -1


def taskfile(text):
    tf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write(text)
    tf.close()
    return tf.name


def urls(text):
    seen = []
    for u in URL_RE.findall(text):
        u = u.rstrip(".;:")
        if u not in seen:
            seen.append(u)
    return seen


def answer(c, arm, rep):
    extra, tsec, drv = ARMS[arm]
    tf = taskfile(c["question"] + SUFFIX)
    args = ["-Kind", "fact", "-Slug", "g5-%s-%s-r%d" % (c["id"].lower(), arm, rep), "-TaskFile", tf,
            "-TimeoutSec", str(tsec)] + extra
    t0 = time.time()
    out, rc = ps(args, drv)
    os.unlink(tf)
    m = re.search(r"OUTCOME: (\w+) \((\d+)s\)", out)
    mc = re.search(r"COST: \$([0-9.]+)", out)
    ma = re.search(r"archived: (\S+)", out)
    ans = out.split("--- ANSWER ---", 1)[1].strip() if "--- ANSWER ---" in out else ""
    return {"case": c["id"], "arm": arm, "rep": rep, "outcome": m.group(1) if m else "NO-OUTCOME", "rc": rc,
            "seconds": int(m.group(2)) if m else None, "wall": round(time.time() - t0, 1),
            "claude_usd": float(mc.group(1)) if mc else (0.0 if arm.startswith("gemini") else None),
            "timeout_sec": tsec, "archive": ma.group(1) if ma else None, "answer": ans,
            "raw_tail": "" if ans else out[-1500:]}


def score(c, rec):
    us = urls(rec["answer"])
    prim = [u for u in us if any(d in u.lower() for d in PRIMARY[c["topic"]])]
    out = {"case": rec["case"], "arm": rec["arm"], "rep": rec["rep"], "n_urls": len(us), "n_primary": len(prim),
           "primary": bool(prim)}
    if rec["outcome"] != "ANSWERED" or not rec["answer"].strip():
        out.update(grade="wrong", reason="no answer (%s)" % rec["outcome"], scorer_usd=0.0, label=None)
        return out
    label = hashlib.md5(os.urandom(8)).hexdigest()[:6].upper()
    tf = taskfile(TEMPLATE.format(q=c["question"], k=c["known_answer"], kp="; ".join(c["key_points"]), label=label,
                                  a=rec["answer"]))
    so, _ = ps(["-Agent", "claude", "-Kind", "fact", "-Model", "sonnet", "-Effort", "low",
                "-Slug", "g5-score-%s-%s" % (rec["case"].lower(), label.lower()), "-TaskFile", tf, "-TimeoutSec", "180"],
               260)
    os.unlink(tf)
    m = re.search(r"GRADE:\s*\**\s*(correct|partly|wrong)", so, re.I)
    r = re.search(r"REASON:\s*(.+)", so)
    mc = re.search(r"COST: \$([0-9.]+)", so)
    out.update(grade=m.group(1).lower() if m else "unscored", reason=r.group(1).strip()[:300] if r else so[-300:],
               scorer_usd=float(mc.group(1)) if mc else None, label=label)
    return out


def worker(arm, rep):
    n = 0
    for c in CASES:
        fn = "%s_%s_r%d.json" % (c["id"], arm, rep)
        ap, sp = os.path.join(AD, fn), os.path.join(SD, fn)
        if os.path.exists(ap):
            rec = json.load(open(ap, encoding="utf-8"))
        else:
            rec = answer(c, arm, rep)
            json.dump(rec, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if not os.path.exists(sp):
            s = score(c, rec)
            json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        else:
            s = json.load(open(sp, encoding="utf-8"))
        with LOCK:
            print("CELL %s %s r%d outcome=%s secs=%s usd=%s grade=%s urls=%d primary=%s" % (
                c["id"], arm, rep, rec["outcome"], rec["seconds"], rec["claude_usd"], s["grade"], s["n_urls"],
                s["primary"]), flush=True)
        n += 1
    return n


if __name__ == "__main__":
    os.makedirs(AD, exist_ok=True)
    os.makedirs(SD, exist_ok=True)
    jobs = [(a, r) for a in ARMS for r in (1, 2)]
    with cf.ThreadPoolExecutor(len(jobs)) as ex:
        list(ex.map(lambda j: worker(*j), jobs))
    subprocess.run([sys.executable, os.path.join(HERE, "report_g2.py")], cwd=ROOT)
    npass = nfail = 0
    ff = None
    for c in CASES:
        for a, r in jobs:
            fn = "%s_%s_r%d.json" % (c["id"], a, r)
            rec = json.load(open(os.path.join(AD, fn), encoding="utf-8"))
            s = json.load(open(os.path.join(SD, fn), encoding="utf-8"))
            if rec["outcome"] == "ANSWERED" and s["grade"] != "unscored":
                npass += 1
            else:
                nfail += 1
                ff = ff or "%s %s r%d %s/%s" % (c["id"], a, r, rec["outcome"], s["grade"])
    rp = os.path.join(HERE, "report_g2.md")
    arts = [{"path": os.path.relpath(p, ROOT), "md5": hashlib.md5(open(p, "rb").read()).hexdigest()}
            for p in (rp, os.path.join(HERE, "cases_g2.json")) if os.path.exists(p)]
    print(protocol.result_line(protocol.make_result(npass, nfail, ff, arts)), flush=True)
