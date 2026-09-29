"""decbench scorer + report writer (card chat-B1). Two independent scores per arm-run:

  mechanical: every rubric item is hit when ANY of its regexes matches the answer text (case-insensitive) -> 1 / 0.
  blind:      one scorer cell per case (claude-opus-5-5 / high, no tools, empty cwd) sees the question, the reference
              answer, the rubric item TEXTS and the answers under shuffled labels (arm, model, repeat hidden) and returns
              0 / 0.5 / 1 per item as JSON.
  score = mean(must_hit) - 0.5 * max(forbidden), floored at 0; bonus is reported beside it, never added.
Disagreements = items where |mechanical - blind| >= 0.5.
"""
import json
import os
import random
import re
import statistics as st

ITEMS = ("must_hit", "forbidden", "bonus")


def mechanical(answer, rubric):
    out = {}
    for k in ITEMS:
        for it in rubric.get(k, []):
            out[it["id"]] = 1.0 if any(re.search(r, answer or "", re.I) for r in it["re"]) else 0.0
    return out


def combine(item_scores, rubric):
    if not item_scores:
        return None
    mh = [item_scores.get(i["id"], 0.0) for i in rubric["must_hit"]]
    fb = [item_scores.get(i["id"], 0.0) for i in rubric.get("forbidden", [])]
    bo = [item_scores.get(i["id"], 0.0) for i in rubric.get("bonus", [])]
    return {"score": round(max(0.0, st.mean(mh) - 0.5 * (max(fb) if fb else 0.0)), 3),
            "must": round(st.mean(mh), 3), "forbidden": max(fb) if fb else 0.0,
            "bonus": round(st.mean(bo), 3) if bo else None}


def blind_prompt(case, question, answers, seed):
    """answers: {run_key: text}. Returns (prompt, {label: run_key})."""
    keys = sorted(answers)
    random.Random(seed).shuffle(keys)
    labels = {chr(65 + i): k for i, k in enumerate(keys)}
    r = case["rubric"]
    items = "\n".join("%s [%s]: %s" % (it["id"], k, it["text"]) for k in ITEMS for it in r.get(k, []))
    body = "\n\n".join("=== ANSWER %s ===\n%s" % (lab, (answers[k] or "(empty answer)").strip()[:9000])
                       for lab, k in labels.items())
    p = ("You are a BLIND SCORER for a benchmark. You do not know which model or method wrote each answer.\n"
         "Score every answer against every rubric item: 1 = fully satisfied, 0.5 = partly, 0 = not at all. For items "
         "marked [forbidden], 1 means the answer COMMITS that error. Judge meaning, not keywords. Use no tools.\n\n"
         "QUESTION GIVEN TO THE ANSWERERS:\n%s\n\nREFERENCE ANSWER (known from later evidence):\n%s\n\nRUBRIC ITEMS:\n%s"
         "\n\n%s\n\nOutput ONLY one JSON object, no prose, of the form "
         "{\"A\": {\"M1\": 1, \"F1\": 0, \"B1\": 0.5, ...}, \"B\": {...}} with every label and every item id.") % (
        question, case["known_answer"], items, body)
    return p, labels


def parse_blind(text, labels, rubric):
    ids = [it["id"] for k in ITEMS for it in rubric.get(k, [])]
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {}
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return {}
    out = {}
    for lab, key in labels.items():
        row = d.get(lab) or {}
        out[key] = {i: float(row[i]) for i in ids if isinstance(row.get(i), (int, float))}
    return out


def aggregate(records, cases):
    """records: list of arm-run dicts (case, arm, rep, usd, minutes, turns, tools, mech, blind)."""
    per_arm = {}
    for r in records:
        a = per_arm.setdefault(r["arm"], {"n": 0, "mech": [], "blind": [], "min": [], "usd": 0.0, "turns": [],
                                          "tools": [], "invalid": 0})
        if r.get("invalid"):
            a["invalid"] += 1
            continue
        a["n"] += 1
        rub = cases[r["case"]]["rubric"]
        mc, bc = combine(r.get("mech") or {}, rub), combine(r.get("blind") or {}, rub)
        a["mech"].append(mc["score"] if mc else 0.0)
        if bc:
            a["blind"].append(bc["score"])
        a["min"].append(r.get("minutes") or 0.0)
        a["usd"] += r.get("usd") or 0.0
        a["turns"].append(r.get("turns") or 0)
        a["tools"].append(r.get("tools") or 0)
    out = {}
    for arm, a in per_arm.items():
        mean = (lambda xs: round(st.mean(xs), 3) if xs else None)
        out[arm] = {"n": a["n"], "invalid": a["invalid"], "mech_mean": mean(a["mech"]), "blind_mean": mean(a["blind"]),
                    "minutes_mean": mean(a["min"]), "usd_total": round(a["usd"], 2),
                    "usd_per_run": round(a["usd"] / a["n"], 3) if a["n"] else None,
                    "turns_mean": mean(a["turns"]), "tools_mean": mean(a["tools"])}
    return out


def disagreements(records):
    d = []
    for r in records:
        for i, v in (r.get("mech") or {}).items():
            b = (r.get("blind") or {}).get(i)
            if b is not None and abs(v - b) >= 0.5:
                d.append("%s %s r%s %s mech %.1f blind %.1f" % (r["case"], r["arm"], r["rep"], i, v, b))
    return d


def write_report(path, per_arm, records, dis, header):
    L = ["# decbench report", "", header, "", "| arm | n | invalid | blind mean | mech mean | min/run | usd total | usd/run "
         "| turns | tool calls |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm, a in sorted(per_arm.items()):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            arm, a["n"], a["invalid"], a["blind_mean"], a["mech_mean"], a["minutes_mean"], a["usd_total"],
            a["usd_per_run"], a["turns_mean"], a["tools_mean"]))
    L += ["", "## Arm-runs", "", "| case | arm | rep | usd | min | mech | blind |", "|---|---|---|---|---|---|---|"]
    for r in sorted(records, key=lambda x: (x["case"], x["arm"], x["rep"])):
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (r["case"], r["arm"], r["rep"], r.get("usd"), r.get("minutes"),
                                                         json.dumps(r.get("mech")), json.dumps(r.get("blind"))))
    L += ["", "## Mechanical vs blind disagreements (|diff| >= 0.5)", ""] + ["- " + x for x in dis or ["none"]]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
