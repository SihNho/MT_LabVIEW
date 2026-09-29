"""ucbench scorer + report (card chat-B3). Set-valued tasks: the answer is a list of CLAIMS, the key a list of ITEMS.

  claims      lines `CLAIM <n>: ... | EVIDENCE: ...` parsed from the final answer (the format is in every prompt).
  mechanical  key item k is FOUND when one claim hits every regex GROUP of k (a group = any-of regexes).
  blind       one claude-opus-5-5/high scorer cell PER ANSWER, run read-only in a fresh worktree of the task's base,
              sees the question, the key items and the numbered claims (arm unknown; agent / workflow wording
              stripped) and returns {"key": {"K1": [claim numbers]}, "extra": {"<n>": "real" | "not_real"}} - every
              claim that matches no key item is checked against the files.
  recall      = key items found / key size (blind; mechanical beside it)
  precision   = (claims matched to a key item + extra claims judged real) / claims judged
  false       = extra claims judged not_real
"""
import json
import re
import statistics as st

CLAIM_RE = re.compile(r"^\s*(?:[-*]\s*)?\**CLAIM\s+(\d+)\**\s*[:.)]\s*(.*)$", re.I)
ARM_WORDS = re.compile(r"\b(sub-?agents?|agents?|workflows?|orchestrat\w*|fan-?out|verifiers?|skeptics?|critics?|"
                       r"finders?|synthesi[sz]\w*|runId|wf_[0-9a-f-]+|parallel(?:ly)?|pipeline[sd]?|lens(?:es)?)\b", re.I)


def parse_claims(answer):
    out, cur = [], None
    for ln in (answer or "").splitlines():
        m = CLAIM_RE.match(ln)
        if m:
            cur = {"n": int(m.group(1)), "text": m.group(2).strip()}
            out.append(cur)
        elif cur is not None and ln.strip() and not re.match(r"^\s*CLAIMS\s*:", ln, re.I):
            if len(cur["text"]) < 1500:
                cur["text"] += " " + ln.strip()
        elif re.match(r"^\s*CLAIMS\s*:", ln, re.I):
            cur = None
    seen, uniq = set(), []
    for c in out:                                   # renumber duplicates so every claim has its own number
        if c["n"] in seen:
            c["n"] = max(seen) + 1
        seen.add(c["n"])
        uniq.append(c)
    return uniq


def strip_arm(text):
    return ARM_WORDS.sub("[method]", text or "")


def _hit(claim_text, groups):
    return all(any(re.search(r, claim_text, re.I) for r in g) for g in groups)


def mechanical(answer, task):
    claims = parse_claims(answer)
    return {k["id"]: next((c["n"] for c in claims if _hit(c["text"], k["re"])), None) for k in task["key"]}


COUNT_RE = re.compile(r"^\s*(?:[-*]\s*)?`?COUNT\s+`?([a-z]+(?:-[a-z]+)+)`?\s*[=:]\s*(\d+)", re.I)


def count_score(answer, task):
    """L3 (card chat-B4): `COUNT <slug> = <n>` lines vs the key's per-slug counts -> exact / key slugs, plus the
    COUNT lines naming a slug outside the key. None for a task without counts."""
    kc = task.get("counts")
    if not kc:
        return None
    got = {}
    for ln in (answer or "").splitlines():
        m = COUNT_RE.match(ln)
        if m:
            got[m.group(1).lower()] = int(m.group(2))
    exact = sorted(s for s, n in kc.items() if got.get(s) == n)
    return {"slugs_key": len(kc), "count_lines": len(got), "exact": len(exact),
            "count_acc": round(len(exact) / len(kc), 3), "wrong": {s: [got[s], kc[s]] for s in kc if s in got and
                                                                   got[s] != kc[s]},
            "missing": sorted(s for s in kc if s not in got), "outside_key": sorted(s for s in got if s not in kc)}


def key_regex_selfcheck(task):
    """each key item's regex groups must compile and all hit the item's own reference text."""
    bad = []
    for k in task["key"]:
        try:
            if not _hit(k["ref"], k["re"]):
                bad.append("%s regex misses its own ref" % k["id"])
        except re.error as e:
            bad.append("%s bad regex %s" % (k["id"], e))
    return bad


def blind_prompt(task, question, answer_stripped, claims, label):
    items = "\n".join("%s: %s" % (k["id"], k["text"]) for k in task["key"])
    cl = "\n".join("CLAIM %d: %s" % (c["n"], strip_arm(c["text"])[:1200]) for c in claims) or "(no claims parsed)"
    return ("You are a BLIND SCORER for a benchmark (answer %s). You do not know which model or method wrote the answer.\n"
            "The current directory is the repository exactly as the answerer saw it. You may use Read, Grep and Glob "
            "(read-only) to CHECK claims. Do not use git.\n\n"
            "QUESTION GIVEN TO THE ANSWERER:\n%s\n\n"
            "KEY - the items known (from later evidence) to be correct answers:\n%s\n\n"
            "THE ANSWER'S CLAIMS:\n%s\n\n"
            "Do two things.\n"
            "1. For every key item, list the claim numbers that state that SAME item (same finding; for a pair of "
            "statements, both sides must be identified - a line number within +-3 of the key's counts, a file:line on "
            "a line holding the quoted text counts too). An empty list if no claim states it.\n"
            "2. For every claim that matches NO key item, open the cited files and judge it: \"real\" if it is a true "
            "and relevant answer to the question given these files (a genuine additional item), \"not_real\" if it is "
            "false, unsupported by the files, a duplicate of another claim, or not what the question asked.\n\n"
            "Output ONLY one JSON object, no prose, of the form "
            "{\"key\": {\"K1\": [3], \"K2\": [], ...}, \"extra\": {\"5\": \"real\", \"7\": \"not_real\", ...}} with "
            "every key id, and every unmatched claim number under extra.") % (label, question, items, cl)


def parse_blind(text, task, claims):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {}
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return {}
    kid = [k["id"] for k in task["key"]]
    key = d.get("key") or {}
    if not all(k in key for k in kid):
        return {}
    ns = {c["n"] for c in claims}
    out = {"key": {k: sorted({int(x) for x in (key.get(k) or []) if str(x).isdigit() and int(x) in ns}) for k in kid},
           "extra": {}}
    for n, v in (d.get("extra") or {}).items():
        if str(n).isdigit() and int(n) in ns:
            out["extra"][int(n)] = "real" if str(v).lower().startswith("real") else "not_real"
    return out


def metrics(task, claims, mech, blind):
    kn = len(task["key"])
    r = {"key_n": kn, "claims_n": len(claims),
         "recall_mech": round(sum(1 for v in mech.values() if v) / kn, 3) if kn else None}
    if blind:
        matched_claims = {n for v in blind["key"].values() for n in v}
        found = sum(1 for v in blind["key"].values() if v)
        extra = {n: v for n, v in blind["extra"].items() if n not in matched_claims}
        real = sum(1 for v in extra.values() if v == "real")
        judged = len(matched_claims) + len(extra)
        r.update({"recall": round(found / kn, 3) if kn else None, "found": found,
                  "precision": round((len(matched_claims) + real) / judged, 3) if judged else None,
                  "extra_real": real, "false_claims": sum(1 for v in extra.values() if v == "not_real"),
                  "unjudged": max(0, len(claims) - judged)})
    return r


def aggregate(recs):
    per = {}
    for r in recs:
        a = per.setdefault(r["arm"], {"n": 0, "invalid": 0, "recall": [], "recall_mech": [], "precision": [],
                                      "false": [], "usd": 0.0, "min": [], "subs": [], "wf": [], "out_tok": []})
        if r.get("invalid"):
            a["invalid"] += 1
            continue
        a["n"] += 1
        s = r.get("score") or {}
        for k, src in (("recall", "recall"), ("recall_mech", "recall_mech"), ("precision", "precision"),
                       ("false", "false_claims")):
            if s.get(src) is not None:
                a[k].append(s[src])
        a["usd"] += r.get("usd") or 0.0
        a["min"].append(r.get("minutes") or 0.0)
        a["subs"].append((r.get("calls") or {}).get("sub_agents", 0))
        a["wf"].append((r.get("top_tool_uses") or {}).get("Workflow", 0))
        a["out_tok"].append((r.get("tokens") or {}).get("outputTokens", 0))
    mean = (lambda xs: round(st.mean(xs), 3) if xs else None)
    return {arm: {"n": a["n"], "invalid": a["invalid"], "recall": mean(a["recall"]), "recall_mech": mean(a["recall_mech"]),
                  "precision": mean(a["precision"]), "false_claims": mean(a["false"]), "usd_total": round(a["usd"], 2),
                  "usd_per_run": round(a["usd"] / a["n"], 3) if a["n"] else None, "minutes_mean": mean(a["min"]),
                  "sub_agents_mean": mean(a["subs"]), "workflow_calls_mean": mean(a["wf"]),
                  "output_tokens_mean": mean(a["out_tok"])} for arm, a in per.items()}


def write_report(path, per_arm, recs, header):
    L = ["# ucbench report", "", header, "",
         "| arm | n | invalid | recall (blind) | recall (mech) | precision | false claims | usd/run | min/run | "
         "sub-agents | Workflow calls | out tokens |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm, a in sorted(per_arm.items()):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            arm, a["n"], a["invalid"], a["recall"], a["recall_mech"], a["precision"], a["false_claims"],
            a["usd_per_run"], a["minutes_mean"], a["sub_agents_mean"], a["workflow_calls_mean"], a["output_tokens_mean"]))
    L += ["", "## Arm-runs", "", "| task | arm | rep | usd | min | claims | recall | recall mech | precision | false | "
          "sub-agents | scorer label |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(recs, key=lambda x: (x["task"], x["arm"], x["rep"])):
        s = r.get("score") or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["task"], r["arm"], r["rep"], r.get("usd"), r.get("minutes"), s.get("claims_n"), s.get("recall"),
            s.get("recall_mech"), s.get("precision"), s.get("false_claims"), (r.get("calls") or {}).get("sub_agents"),
            r.get("scorer_label")))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def stub_expectations(recs):
    """--stub dry run: the stub answers 2 claims (CLAIM 1 = the first key item's ref, CLAIM 2 = a false one), the stub
    scorer maps K1 -> [1] and claim 2 -> not_real; the UC stub emits one Workflow tool_use and 2 sub-agent calls."""
    bad = []
    for r in recs:
        if r.get("invalid"):
            continue
        s = r.get("score") or {}
        exp_recall = round(1 / s["key_n"], 3) if s.get("key_n") else None
        if s.get("claims_n") != 2 or s.get("recall") != exp_recall or s.get("precision") != 0.5 \
                or s.get("false_claims") != 1 or s.get("recall_mech") != exp_recall:
            bad.append("stub score %s %s: %s" % (r["task"], r["arm"], s))
        wf, subs = (r.get("top_tool_uses") or {}).get("Workflow", 0), (r.get("calls") or {}).get("sub_agents", 0)
        if (r["arm"] == "UC") != (wf == 1 and subs == 2):
            bad.append("stub accounting %s %s: workflow %s subagents %s" % (r["task"], r["arm"], wf, subs))
    return bad
