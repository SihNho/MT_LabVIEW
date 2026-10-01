"""score.py - card chat-G1 Part B: blind grade of every answer in answers/*.json.

Blind: the scorer (peer.ps1 -Agent claude -Kind fact -Model sonnet -Effort low, thin via --safe-mode) sees only the
question, the known answer + key points, and ONE answer under a random label; never the arm, repeat or model. Answers
are graded in shuffled order, 4 at a time. Every scorer exchange is archived by peer.ps1 (archive/peer/..-g1-score-*).
Also computed here, mechanically: unique source URLs, and whether >=1 is a primary source (vendor domain per topic).

PREDICTION CONTRACT: one scores/<answer>.json per answer file with grade in {correct, partly, wrong}; a scorer call
that yields no GRADE line is recorded as grade 'unscored' and counted as a fail in the RESULT line.
"""
import concurrent.futures as cf, hashlib, json, os, random, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]}
PRIMARY = {"LabVIEW VI Scripting": ["ni.com"], "LabVIEW VI Server": ["ni.com"], "NI-IMAQdx": ["ni.com"],
           "Windows PowerShell": ["microsoft.com", "github.com/powershell", "github.com/microsoftdocs"],
           "Windows NTFS": ["microsoft.com", "github.com/microsoftdocs"]}
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'`|,]+")

TEMPLATE = """You are grading ONE answer to a technical question against a known, machine-verified answer.
Do NOT search the web and do NOT use any tool; grade only from the text below.

QUESTION:
{q}

KNOWN ANSWER (verified on the machine / vendor files):
{k}
KEY POINTS: {kp}

ANSWER {label} TO GRADE:
<<<
{a}
>>>

Grade: correct = every key point right and nothing contradicting the known answer; partly = the main point right
but a key point missing or wrong; wrong = the main point wrong, or no usable answer.
Reply with exactly two lines:
GRADE: correct|partly|wrong
REASON: <one sentence>"""


def urls(text):
    seen = []
    for u in URL_RE.findall(text):
        u = u.rstrip(".;:")
        if u not in seen:
            seen.append(u)
    return seen


def grade(fn):
    rec = json.load(open(fn, encoding="utf-8"))
    c = CASES[rec["case"]]
    us = urls(rec["answer"])
    prim = [u for u in us if any(d in u.lower() for d in PRIMARY[c["topic"]])]
    out = {"file": os.path.basename(fn), "case": rec["case"], "arm": rec["arm"], "rep": rec["rep"],
           "n_urls": len(us), "n_primary": len(prim), "primary": bool(prim)}
    if rec["outcome"] != "ANSWERED" or not rec["answer"].strip():
        out.update(grade="wrong", reason="no answer (%s)" % rec["outcome"], scorer_usd=0.0, label=None)
        return out
    label = hashlib.md5(os.urandom(8)).hexdigest()[:6].upper()
    body = TEMPLATE.format(q=c["question"], k=c["known_answer"], kp="; ".join(c["key_points"]), label=label,
                           a=rec["answer"])
    tf = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write(body)
    tf.close()
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, "tools", "peer.ps1"),
           "-Agent", "claude", "-Kind", "fact", "-Model", "sonnet", "-Effort", "low",
           "-Slug", "g1-score-%s-%s" % (rec["case"].lower(), label.lower()), "-TaskFile", tf.name, "-TimeoutSec", "180"]
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=260)
        so = p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        so = ""
    os.unlink(tf.name)
    m = re.search(r"GRADE:\s*\**\s*(correct|partly|wrong)", so, re.I)
    r = re.search(r"REASON:\s*(.+)", so)
    mc = re.search(r"COST: \$([0-9.]+)", so)
    out.update(grade=m.group(1).lower() if m else "unscored", reason=r.group(1).strip()[:300] if r else so[-300:],
               scorer_usd=float(mc.group(1)) if mc else None, label=label)
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "scores"), exist_ok=True)
    files = sorted(os.path.join(HERE, "answers", f) for f in os.listdir(os.path.join(HERE, "answers")) if f.endswith(".json"))
    todo = [f for f in files if not os.path.exists(os.path.join(HERE, "scores", os.path.basename(f)))]
    random.shuffle(todo)
    npass = nfail = 0
    ff = None
    with cf.ThreadPoolExecutor(4) as ex:
        for res in ex.map(grade, todo):
            json.dump(res, open(os.path.join(HERE, "scores", res["file"]), "w", encoding="utf-8"), indent=1)
            print("SCORE %s %s r%d -> %s urls=%d primary=%s" % (res["case"], res["arm"], res["rep"], res["grade"],
                                                                 res["n_urls"], res["primary"]), flush=True)
            if res["grade"] == "unscored":
                nfail += 1
                ff = ff or res["file"]
            else:
                npass += 1
    print(protocol.result_line(protocol.make_result(npass, nfail, ff, [])), flush=True)
