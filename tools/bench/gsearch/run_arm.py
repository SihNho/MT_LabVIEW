"""run_arm.py - card chat-G1 Part B: one arm x one repeat over every case in cases.json.

Prior art checked: tools/bench/matbench/ (replays material cards, not web questions) and tools/peer.ps1 (-Kind fact
routing, archive). Nothing existing runs the same question through several peer arms, so this thin driver only
loops peer.ps1; it adds no routing of its own.

Arms:  gemini      peer.ps1 -Agent gemini -Kind fact             (agy default model)
       gemini-pro  peer.ps1 -Agent gemini -Kind fact -Model gemini-3.1-pro-high   (listed by `agy models`)
       claude      peer.ps1 -Kind fact                           (role table default: claude fact role)
Every exchange is archived by peer.ps1 (archive/peer/<date>-g1-<case>-<arm>-r<rep>.md).

PREDICTION CONTRACT: one answer file per case (tools/bench/gsearch/answers/<case>_<arm>_r<rep>.json);
outcome ANSWERED for every case (a TIMEOUT/ERROR is recorded, not retried); the RESULT line counts ANSWERED as pass.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SUFFIX = "\n\nSearch the web and cite the URL of every source you used."

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True, choices=["gemini", "gemini-pro", "claude"])
ap.add_argument("--rep", type=int, required=True)
ap.add_argument("--only", default="")
a = ap.parse_args()

cases = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]
if a.only:
    cases = [c for c in cases if c["id"] in a.only.split(",")]
os.makedirs(os.path.join(HERE, "answers"), exist_ok=True)
npass = nfail = 0
first_fail = None
arts = []
for c in cases:
    slug = "g1-%s-%s-r%d" % (c["id"].lower(), a.arm, a.rep)
    tf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write(c["question"] + SUFFIX)
    tf.close()
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, "tools", "peer.ps1"),
           "-Kind", "fact", "-Slug", slug, "-TaskFile", tf.name, "-TimeoutSec", "300"]
    if a.arm.startswith("gemini"):
        cmd += ["-Agent", "gemini"]
    if a.arm == "gemini-pro":
        cmd += ["-Model", "gemini-3.1-pro-high"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=420)
        out = p.stdout.decode("utf-8", "replace")
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "(driver timeout 420 s)", -1
    wall = round(time.time() - t0, 1)
    os.unlink(tf.name)
    m = re.search(r"OUTCOME: (\w+) \((\d+)s\)", out)
    outcome = m.group(1) if m else "NO-OUTCOME"
    secs = int(m.group(2)) if m else None
    mc = re.search(r"COST: \$([0-9.]+)", out)
    usd = float(mc.group(1)) if mc else (0.0 if a.arm.startswith("gemini") else None)
    ans = out.split("--- ANSWER ---", 1)[1].strip() if "--- ANSWER ---" in out else ""
    ma = re.search(r"archived: (\S+)", out)
    rec = {"case": c["id"], "arm": a.arm, "rep": a.rep, "outcome": outcome, "rc": rc, "seconds": secs,
           "wall": wall, "claude_usd": usd, "archive": ma.group(1) if ma else None, "answer": ans,
           "raw_tail": "" if ans else out[-1500:]}
    fn = os.path.join(HERE, "answers", "%s_%s_r%d.json" % (c["id"], a.arm, a.rep))
    json.dump(rec, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    arts.append({"path": os.path.relpath(fn, ROOT), "md5": hashlib.md5(open(fn, "rb").read()).hexdigest()})
    print("CASE %s arm=%s rep=%d outcome=%s secs=%s usd=%s" % (c["id"], a.arm, a.rep, outcome, secs, usd), flush=True)
    if outcome == "ANSWERED":
        npass += 1
    else:
        nfail += 1
        first_fail = first_fail or "%s %s r%d %s" % (c["id"], a.arm, a.rep, outcome)
print(protocol.result_line(protocol.make_result(npass, nfail, first_fail, arts[:5])), flush=True)
