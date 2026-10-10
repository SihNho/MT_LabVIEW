# ---
# labview: none
# hardware: none
# ---
"""score_x7.py - card chat-X7 (experiment 3 of discussion structure-equal-02): blind scoring of arm A (single
hypothesis review, peer.ps1) vs arm B (debate_gdoc discussion) on the three replayed hand-backs.

Prior art checked: no existing blind scorer in tools/ or tools/bench (grep "blind" / "scorer": only the matbench and
assignbench graders, which score a fixed rubric of one arm, not an X/Y pair). The process helpers are CALLED from
tools/debate_relay.py (run_killable, codex_js, summary) - not copied.

Prediction contract: for n in 1..3 the A answer (archive/peer/<date>-reviewbench-<n>.md, section "## Answer") and the
B answer (tools/bench/reviewbench/disc_<n>/summary.json + relay/state.json) both exist and are non-empty; the scorer
returns one JSON object with keys X and Y, each {cause, test, wrong_claims, actionable}; 3 claude scorings succeed (and
1 GPT scoring of case 1 when --gpt1). Each failed expectation is one gate fail.

Blinding: the mapping X/Y -> arm is drawn with random.SystemRandom, held in --mapdir (outside the project, %TEMP%) during
scoring and copied to tools/bench/reviewbench/mapping_x7.json only after every scoring call has returned. The scorer
reads no file under archive/, docs/ or tools/bench/reviewbench/ (deny rules); answers and truth are inlined in its prompt.

    py -u tools/bench/reviewbench/score_x7.py --truthdir <tmp> --mapdir <tmp> [--gpt1] [--dry]
"""
import argparse
import glob
import json
import os
import random
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import debate_relay  # noqa: E402  (run_killable, codex_js, summary)
import protocol  # noqa: E402

RUBRIC = """You are a blind scorer. Two anonymous answers (X and Y) were given to the same failure-review question:
"What is the most likely cause of this failure, what is the strongest alternative, and what is the cheapest test that
tells them apart?" The TRUTH below is what was decided later and which card then passed. Score each answer against it:

- cause: "yes" if the answer's most likely cause is the truth's cause, "partial" if it names part of it or puts it as
  the alternative / with the wrong primary fix, "no" otherwise.
- test: "yes" if its cheapest discriminating test is the test that later decided it (same check, same object), "partial"
  if it would discriminate but is a different or much larger test, "no" otherwise.
- wrong_claims: count the factual claims about the code / logs / graph that are wrong. You MAY open files under
  tools/ (not tools/bench/reviewbench/), e.g. tools/stagexec.py or a cited log, with the Read tool to check a file:line
  claim; note that tools/stagexec.py today is LATER than at the failure, so a line-number drift of a few lines is not
  wrong. List each wrong claim with the file:line you checked.
- actionable: "yes" if a single next task card could be written directly from the answer (clear change + check), else "no".
Answers may be in Korean or English; judge content only. Do not try to guess which answer came from which system.

Reply with ONE JSON object and nothing else:
{"X":{"cause":"yes|partial|no","test":"yes|partial|no","wrong_claims":0,"wrong_list":[{"claim":"","checked":"file:line","why":""}],"actionable":"yes|no","note":"<=200 chars"},
 "Y":{...same keys...}}
"""

PARTY_RE = re.compile(r"\b(Claude|GPT|Codex|Opus|ChatGPT)\b|클로드|코덱스", re.I)


def answer_a(n):
    """Arm A answer: the '## Answer' section of the archived hypothesis review for case n -> (text, meta)."""
    fs = sorted(glob.glob(os.path.join(ROOT, "archive", "peer", "*-reviewbench-%d.md" % n)))
    if not fs:
        return "", {}
    t = open(fs[-1], encoding="utf-8").read()
    body = t.split("\n## Answer", 1)[-1].split("\n## What was done with it", 1)[0]
    meta = {"file": os.path.relpath(fs[-1], ROOT).replace("\\", "/")}
    m = re.search(r"\*\*cost:\*\*\s*\$([\d.]+).*?\((\d+)s", t)
    if m:
        meta.update(usd=float(m.group(1)), secs=int(m.group(2)))
    return body.strip(), meta


def answer_b(n):
    """Arm B answer: the discussion summary's agreed items + experiment + open; when nothing was agreed, the last
    round's two messages (STATE lines removed) are appended -> (text, meta)."""
    d = os.path.join(HERE, "disc_%d" % n, "relay")
    s = debate_relay.summary(d)
    parts = []
    if s["agreed"]:
        parts.append("Agreed conclusions:\n" + "\n".join("- " + x for x in s["agreed"]))
    if s["experiment"]:
        parts.append("Proposed discriminating test:\n" + "\n".join("- " + x for x in s["experiment"]))
    if s["open"]:
        parts.append("Still open:\n" + "\n".join("- " + x for x in s["open"]))
    used_last = False
    if not s["agreed"]:
        st = json.load(open(os.path.join(d, "state.json"), encoding="utf-8"))
        for i, msg in enumerate((st.get("last_msg") or {}).values()):
            parts.append("Final statement %d:\n%s" % (i + 1, debate_relay.STATE_RE.sub("", msg or "").strip()))
        used_last = True
    meta = {"rounds": s["rounds"], "converged": s["converged"], "claude_usd": s["claude_usd"], "used_last_msgs": used_last}
    return "\n\n".join(parts).strip(), meta


def neutral(t):
    """Strip system names and STATE lines so the scorer cannot tell the arms apart by name."""
    return PARTY_RE.sub("[reviewer]", debate_relay.STATE_RE.sub("", t))


def ask_claude(prompt):
    env = dict(os.environ, BENCH_CELL="1")
    cmd = ["claude", "-p", "--model", "claude-opus-5-5", "--effort", "high", "--output-format", "json",
           "--allowedTools", "Read", "--disallowedTools", "Edit", "Write", "Bash", "PowerShell", "Agent", "NotebookEdit",
           "Grep", "Glob", "WebSearch", "WebFetch", "Read(./archive/**)", "Read(./docs/**)", "Read(./STATUS.md)",
           "Read(./tools/bench/reviewbench/**)", "Read(./tools/bench/cards/**)"]
    t0 = time.time()
    rc, out, err, _ = debate_relay.run_killable(cmd, ROOT, prompt, env, os.path.join(HERE, "STOP_SCORER"), timeout=1200)
    try:
        j = json.loads(out)
        return j.get("result") or "", j.get("total_cost_usd"), round(time.time() - t0)
    except ValueError:
        return "(claude failed rc=%s: %s)" % (rc, (err or out)[:400]), None, round(time.time() - t0)


def ask_gpt(prompt, outfile):
    env = dict(os.environ)
    cmd = ["node", debate_relay.codex_js(), "exec", "--json", "--skip-git-repo-check", "-o", outfile,
           "-s", "danger-full-access", "-m", "gpt-6.1-sol", "-c", 'model_reasoning_effort="high"', "-C", ROOT, "-"]
    t0 = time.time()
    rc, out, err, _ = debate_relay.run_killable(cmd, ROOT, "READ-ONLY: do not change any file or run anything; only "
                                                "read files to check claims.\n\n" + prompt, env,
                                                os.path.join(HERE, "STOP_SCORER"), timeout=1200)
    usage = None
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        u = ev.get("usage") or (ev.get("msg") or {}).get("usage")
        if u:
            usage = u
    try:
        return open(outfile, encoding="utf-8").read(), usage, round(time.time() - t0)
    except OSError:
        return "(gpt failed rc=%s: %s)" % (rc, (err or out)[:400]), usage, round(time.time() - t0)


def parse(txt):
    m = re.search(r"\{.*\}", txt or "", re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--truthdir", required=True)
    ap.add_argument("--mapdir", required=True)
    ap.add_argument("--gpt1", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    ok, fails, rng = 0, [], random.SystemRandom()
    mapping, results, arms = {}, {}, {}
    for n in (1, 2, 3):
        ta, ma = answer_a(n)
        tb, mb = answer_b(n)
        arms[n] = {"A": ma, "B": mb, "A_chars": len(ta), "B_chars": len(tb)}
        for lab, t in (("A%d answer non-empty" % n, ta), ("B%d answer non-empty" % n, tb)):
            if t:
                ok += 1
            else:
                fails.append(lab)
        x_is_a = rng.random() < 0.5
        mapping[n] = {"X": "A" if x_is_a else "B", "Y": "B" if x_is_a else "A"}
        xy = {"X": ta if x_is_a else tb, "Y": tb if x_is_a else ta}
        os.makedirs(os.path.join(a.mapdir, "blind"), exist_ok=True)
        for k in xy:
            open(os.path.join(a.mapdir, "blind", "case_%d_%s.md" % (n, k)), "w", encoding="utf-8").write(neutral(xy[k]))
        truth = open(os.path.join(a.truthdir, "truth_%d.md" % n), encoding="utf-8").read()
        case = open(os.path.join(HERE, "case_%d.md" % n), encoding="utf-8").read()
        prompt = "%s\n\n## CASE (what both reviewers saw)\n%s\n\n## TRUTH\n%s\n\n## ANSWER X\n%s\n\n## ANSWER Y\n%s\n" % (
            RUBRIC, case, truth, neutral(xy["X"]), neutral(xy["Y"]))
        open(os.path.join(a.mapdir, "prompt_%d.md" % n), "w", encoding="utf-8").write(prompt)
        if a.dry:
            continue
        txt, usd, secs = ask_claude(prompt)
        sc = parse(txt)
        results.setdefault(n, {})["claude"] = {"raw": txt[-3000:], "score": sc, "usd": usd, "secs": secs}
        print("SCORED case %d claude usd %s secs %s parsed %s" % (n, usd, secs, bool(sc)), flush=True)
        (ok, fails) = (ok + 1, fails) if sc and "X" in sc and "Y" in sc else (ok, fails + ["claude score case %d" % n])
        if a.gpt1 and n == 1:
            txt, usage, secs = ask_gpt(prompt, os.path.join(a.mapdir, "gpt_score_1.txt"))
            sc = parse(txt)
            results[n]["gpt"] = {"raw": txt[-3000:], "score": sc, "usage": usage, "secs": secs}
            print("SCORED case 1 gpt secs %s usage %s parsed %s" % (secs, usage, bool(sc)), flush=True)
            (ok, fails) = (ok + 1, fails) if sc and "X" in sc and "Y" in sc else (ok, fails + ["gpt score case 1"])
    # un-blind only now: every scoring call has returned
    json.dump(mapping, open(os.path.join(a.mapdir, "mapping_x7.json"), "w"), indent=1)
    out = {"schema": "reviewbench-x7/1", "arms": arms, "mapping": mapping, "scores": results, "dry": a.dry}
    if not a.dry:
        shutil.copy(os.path.join(a.mapdir, "mapping_x7.json"), os.path.join(HERE, "mapping_x7.json"))
        bd = os.path.join(HERE, "blind")
        os.makedirs(bd, exist_ok=True)
        for f in glob.glob(os.path.join(a.mapdir, "blind", "*.md")):
            shutil.copy(f, bd)
        unblind = {}
        for n, r in results.items():
            for who, v in r.items():
                for k in ("X", "Y"):
                    if v.get("score") and k in v["score"]:
                        unblind.setdefault(str(n), {}).setdefault(who, {})[mapping[n][k]] = v["score"][k]
        out["unblinded"] = unblind
        json.dump(out, open(os.path.join(HERE, "scores_x7.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(protocol.result_line(protocol.make_result(ok, len(fails), fails[0] if fails else None)), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
