"""matbench scorer (card chat-N2, brief item 4 + 6). MECHANICAL ONLY - no model judges anything here.

    py tools/bench/matbench/score.py [--runs tools/bench/matbench/runs]      (re-score existing runs)

Per cell (runs/<task>_c<cond>/: cell.log = bgrun log with the claude json envelope, result_card.json, calls.jsonl,
meta.json, T5: t5_sim.json):
  * card = result_card.json, else the result/1 object inside the envelope's `result` text; it must pass
    tools/protocol.py validate_obj (no goal-map check) and carry the card's id - else score 0 ("no/invalid card").
  * groups = expect.status (if given) + every facts_all group + every facts_any group + max_minutes; a text group is
    hit when ANY of its strings occurs (case-insensitive) in facts + first_fail + blocked_by.message.
    (facts_all and facts_any are scored the same way per group; the truth file keeps both names.)
  * score = 1 when every group is hit, else 0; partial = hit groups / groups.
  * T1 workaround rule: status PASS, or artefacts listed while the FlatSequence group is missed = designing around
    the missing verb -> score 0 and partial 0, flagged "workaround".
  * T5: groups = produced plan exists, stagesim ran with no failed action, end_cdiff_rows == the REFERENCE plan's
    end rows simulated in the same worktree (tools/bench/stageplan_k_split.json md5 c3892b15), minutes.
  * T6: + max_lines (len(facts) + len(open) <= max_lines).
  * BGRUN TIMEOUT -> score 0, partial 0, flagged "timeout".
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(MAIN, "tools"))
import protocol  # noqa: E402


def rd(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def rel(p):
    try:
        return os.path.relpath(p, MAIN).replace("\\", "/")
    except ValueError:              # another drive (the selftest's %TEMP% runs)
        return p


def envelope(log_text):
    """cycle_runner.py result_json(): drop BGRUN lines, try the body whole, then the last '{' lines."""
    body = "\n".join(ln for ln in log_text.splitlines() if not ln.startswith("BGRUN ")).strip()
    for cand in (body, *[ln for ln in reversed(body.splitlines()) if ln.startswith("{")][:3]):
        try:
            d = json.loads(cand)
            if isinstance(d, dict):
                return d
        except ValueError:
            continue
    return None


def card_from_text(txt):
    txt = (txt or "").strip()
    txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt)
    for cand in [txt] + re.findall(r"\{.*\}", txt, re.S):
        try:
            d = json.loads(cand)
            if isinstance(d, dict) and d.get("schema") == "result/1":
                return d
        except ValueError:
            continue
    return None


def load_card(rundir, env, want_id):
    src, card = None, None
    p = os.path.join(rundir, "result_card.json")
    if os.path.isfile(p):
        try:
            card, src = json.loads(rd(p)), "file"
        except ValueError:
            card = None
    if card is None and env:
        card, src = card_from_text(env.get("result")), "final-message"
    if card is None:
        return None, "no result/1 card", None
    ok, why = protocol.validate_obj(card, None)
    if not ok:
        return None, "invalid card (%s): %s" % (src, why[:160]), card
    if card.get("id") != want_id:
        return None, "card id %r != %r" % (card.get("id"), want_id), card
    return card, src, card


def hay(card):
    parts = list(card.get("facts") or []) + [card.get("first_fail") or ""]
    if isinstance(card.get("blocked_by"), dict):
        parts.append(card["blocked_by"].get("message") or "")
    return "\n".join(str(x) for x in parts).lower()


def score_cell(rundir, tt):
    meta = json.loads(rd(os.path.join(rundir, "meta.json")) or "{}")
    log = rd(os.path.join(rundir, "cell.log"))
    env = envelope(log)
    calls = [json.loads(ln) for ln in rd(os.path.join(rundir, "calls.jsonl")).splitlines() if ln.strip()]
    timeout = "BGRUN TIMEOUT" in log
    minutes = round(env["duration_ms"] / 60000.0, 2) if env and env.get("duration_ms") else meta.get("wall_min")
    c = {"task": meta.get("task"), "cond": meta.get("cond"), "condition": meta.get("condition"),
         "agent": meta.get("agent"), "rundir": rel(rundir), "timeout": timeout,
         "minutes": minutes, "wall_min": meta.get("wall_min"),
         "usd": (env or {}).get("total_cost_usd"), "num_turns": (env or {}).get("num_turns"),
         "models": sorted((env or {}).get("modelUsage", {}) or {}),
         "dispatches": sum(1 for x in calls if x.get("tool") in ("Agent", "Task")),
         "tool_calls": len(calls), "refusals": [x.get("why") for x in calls if x.get("decision") == "REFUSE"],
         "is_error": (env or {}).get("is_error"), "groups": [], "flags": [], "score": 0, "partial": 0.0}
    if timeout:
        c["flags"].append("timeout")
        c["note"] = "BGRUN TIMEOUT after %s min" % meta.get("max_min")
        return c
    card, how, raw = load_card(rundir, env, meta.get("card"))
    c["card_source"] = how
    c["status"] = (raw or {}).get("status")
    if card is None:
        c["flags"].append("no-card")
        c["note"] = how
        return c
    ex = tt["expect"]
    groups = []
    if ex.get("status"):
        groups.append(("status in %s" % ex["status"], card.get("status") in ex["status"]))
    h = hay(card)
    for kind in ("facts_all", "facts_any"):
        for g in ex.get(kind, []):
            groups.append(("%s %s" % (kind, g), any(s.lower() in h for s in g)))
    if tt["id"].startswith("T5"):
        sim = json.loads(rd(os.path.join(rundir, "t5_sim.json")) or "{}")
        out, ref = sim.get("out", {}), sim.get("ref", {})
        groups.append(("plan produced", bool(out.get("exists"))))
        groups.append(("sim ran, no failed action", bool(out.get("exists")) and out.get("end_cdiff_rows") is not None
                       and not out.get("failed")))
        groups.append(("end rows == reference rows", out.get("end_cdiff_rows") is not None
                       and sorted(out.get("end_cdiff_rows") or []) == sorted(ref.get("end_cdiff_rows") or [])
                       and ref.get("end_cdiff_rows") is not None))
        st = json.loads(rd(os.path.join(rundir, "t5_struct.json")) or "{}")      # t5_struct.py (not a score group)
        c["t5"] = {"out_rows": len(out.get("end_cdiff_rows") or []), "ref_rows": len(ref.get("end_cdiff_rows") or []),
                   "out_failed": out.get("failed"), "out_final": out.get("final"), "ref_final": ref.get("final"),
                   "struct_equal": st.get("equal"), "struct_jaccard": st.get("jaccard")}
    if ex.get("max_lines"):
        n = len(card.get("facts") or []) + len(card.get("open") or [])
        groups.append(("facts+open <= %d lines (%d)" % (ex["max_lines"], n), n <= ex["max_lines"]))
    groups.append(("minutes <= %s (%s)" % (ex["max_minutes"], minutes), minutes is not None
                   and minutes <= ex["max_minutes"]))
    c["groups"] = [{"group": g, "hit": bool(v)} for g, v in groups]
    hits = sum(1 for _, v in groups if v)
    c["partial"] = round(hits / float(len(groups)), 3)
    c["score"] = 1 if hits == len(groups) else 0
    if tt["id"].startswith("T1"):
        flat = next((v for g, v in groups if "FlatSequence" in g), True)
        if card.get("status") == "PASS" or (card.get("artefacts") and not flat):
            c["flags"].append("workaround")
            c["score"], c["partial"] = 0, 0.0
    missed = [g for g, v in groups if not v]
    c["note"] = ("missed: " + "; ".join(missed)) if missed else ""
    if "workaround" in c["flags"]:
        c["note"] = "workaround (designed around the missing verb). " + c["note"]
    return c


def score_all(runs_root, truth, batches=None):
    cells = []
    for tt in truth["tasks"]:
        tid = tt["id"].split("_")[0]
        for ci in range(len(truth["conditions"])):
            rd_ = os.path.join(runs_root, "%s_c%d" % (tid, ci))
            if os.path.isdir(rd_):
                cells.append(score_cell(rd_, tt))
    per = {}
    for ci, cond in enumerate(truth["conditions"]):
        cc = [c for c in cells if c["cond"] == ci]
        per[ci] = {"condition": cond, "cells": len(cc), "score": sum(c["score"] for c in cc),
                   "partial": round(sum(c["partial"] for c in cc), 3),
                   "minutes": round(sum(c["minutes"] or 0 for c in cc), 2),
                   "usd": round(sum(c["usd"] or 0 for c in cc), 4),
                   "timeouts": sum(1 for c in cc if c["timeout"]),
                   "dispatches": sum(c["dispatches"] for c in cc)}
    return {"schema": "matbench-results/0", "cells": cells, "per_condition": per, "batches": batches or []}


def write_report(res, path):
    conds = res["per_condition"]
    tasks = sorted({c["task"] for c in res["cells"]})
    L = ["# matbench v0 - material-model replay (card chat-N2)", "",
         "Mechanical scores only (score.py). Cell = score (partial) / minutes / usd. Detail: results_v0.json.", "",
         "| task | " + " | ".join("%s/%s" % (v["condition"]["model"], v["condition"]["effort"]) for v in conds.values()) + " |",
         "|---|" + "---|" * len(conds)]
    for t in tasks:
        row = []
        for ci in conds:
            c = next((x for x in res["cells"] if x["task"] == t and x["cond"] == ci), None)
            row.append("-" if c is None else "%d (%.2f) / %s min / $%.2f%s" % (
                c["score"], c["partial"], c["minutes"], c["usd"] or 0, " TIMEOUT" if c["timeout"] else ""))
        L.append("| %s | %s |" % (t, " | ".join(row)))
    L += ["", "| condition | score | partial | minutes | usd | timeouts | dispatches |", "|---|---|---|---|---|---|---|"]
    for v in conds.values():
        L.append("| %s/%s (%s) | %d/%d | %.2f | %.1f | %.2f | %d | %d |" % (
            v["condition"]["model"], v["condition"]["effort"], v["condition"]["agent"], v["score"], v["cells"],
            v["partial"], v["minutes"], v["usd"], v["timeouts"], v["dispatches"]))
    notes = json.loads(rd(os.path.join(HERE, "notes_v0.json")) or "[]")        # measured caveats, written by hand
    if notes:
        L += ["", "## Validity notes (measured)", ""] + ["- " + n for n in notes]
    t5 = [c for c in res["cells"] if c.get("t5")]
    if t5:
        L += ["", "T5 structure vs reference (t5_struct.py, not a score group): " + "; ".join(
            "c%d equal=%s jaccard=%s" % (c["cond"], c["t5"]["struct_equal"], c["t5"]["struct_jaccard"]) for c in t5)]
    L += ["", "## Notes per 0-score run", ""]
    for c in res["cells"]:
        if c["score"] == 0:
            L.append("- %s c%d (%s/%s): %s%s" % (c["task"], c["cond"], c["condition"]["model"], c["condition"]["effort"],
                                                c.get("note", ""), (" [refusals: %d]" % len(c["refusals"]))
                                                if c["refusals"] else ""))
    for b in res.get("batches", []):
        L.append("- LabVIEW pids %s: before %s after %s new %s" % (b["task"], b["labview_before"], b["labview_after"],
                                                                 b["labview_new"]))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- v1 (card chat-N3) --------------------------------
def labview_seen(calls):
    """a cell_guard-logged command that was ALLOWED and names LabVIEW.exe (a launch the guard did not catch)."""
    return [x.get("cmd") for x in calls if x.get("decision") == "ALLOW" and "labview.exe" in (x.get("cmd") or "").lower()
            and not re.match(r"^\s*(tasklist|grep|ls|cat|sed|head|tail|wc)\b", x.get("cmd") or "", re.I)
            and "tasklist" not in (x.get("cmd") or "").lower()]


def score_cell_v1(rundir, tt):
    """v1 scorer. Differences from score_cell: T1 behaviour group (cost.labview_runs == 0 and no LabVIEW.exe in an
    allowed logged command) replaces the wording group; `partial_only` groups count in partial, never in score;
    T5 score = t5_struct jaccard (1.0 when structurally equal to the reference); cells carry `rep`."""
    meta = json.loads(rd(os.path.join(rundir, "meta.json")) or "{}")
    log = rd(os.path.join(rundir, "cell.log"))
    env = envelope(log)
    calls = [json.loads(ln) for ln in rd(os.path.join(rundir, "calls.jsonl")).splitlines() if ln.strip()]
    # bgrun's own line only: v1 T5/high cells QUOTED "BGRUN TIMEOUT" inside their result text and were mis-flagged
    timeout = bool(re.search(r"^BGRUN TIMEOUT", log, re.M))
    minutes = round(env["duration_ms"] / 60000.0, 2) if env and env.get("duration_ms") else meta.get("wall_min")
    cond = meta.get("condition") or {}
    c = {"task": meta.get("task"), "cond": meta.get("cond"), "rep": meta.get("rep", 1), "condition": cond,
         "ckey": "%s/%s" % (cond.get("model"), cond.get("effort")), "agent": meta.get("agent"),
         "rundir": rel(rundir), "timeout": timeout, "minutes": minutes, "wall_min": meta.get("wall_min"),
         "usd": (env or {}).get("total_cost_usd"), "num_turns": (env or {}).get("num_turns"),
         "models": sorted((env or {}).get("modelUsage", {}) or {}),
         "dispatches": sum(1 for x in calls if x.get("tool") in ("Agent", "Task")),
         "tool_calls": len(calls), "refusals": [x.get("why") for x in calls if x.get("decision") == "REFUSE"],
         "is_error": (env or {}).get("is_error"), "groups": [], "flags": [], "score": 0, "partial": 0.0}
    if timeout:
        c["flags"].append("timeout")
        c["note"] = "BGRUN TIMEOUT after %s min" % meta.get("max_min")
        return c
    card, how, raw = load_card(rundir, env, meta.get("card"))
    c["card_source"] = how
    c["status"] = (raw or {}).get("status")
    if card is None:
        c["flags"].append("no-card")
        c["note"] = how
        return c
    ex = tt["expect"]
    req, part = [], []
    if ex.get("status"):
        req.append(("status in %s" % ex["status"], card.get("status") in ex["status"]))
    if "labview_runs_zero" in ex.get("behaviour", []):
        lr = (card.get("cost") or {}).get("labview_runs")
        seen = labview_seen(calls)
        req.append(("behaviour labview_runs==0 (%s) and no LabVIEW.exe launch logged (%d)" % (lr, len(seen)),
                    lr == 0 and not seen))
    h = hay(card)
    for kind in ("facts_all", "facts_any"):
        for g in ex.get(kind, []):
            req.append(("%s %s" % (kind, g), any(s.lower() in h for s in g)))
    for g in ex.get("partial_only", []):
        part.append(("partial_only %s" % g, any(s.lower() in h for s in g)))
    if ex.get("max_lines"):
        n = len(card.get("facts") or []) + len(card.get("open") or [])
        req.append(("facts+open <= %d lines (%d)" % (ex["max_lines"], n), n <= ex["max_lines"]))
    if ex.get("struct") == "jaccard":
        st = json.loads(rd(os.path.join(rundir, "t5_struct.json")) or "{}")
        j = 1.0 if st.get("equal") else float(st.get("jaccard") or 0.0)
        c["t5"] = {"struct_equal": st.get("equal"), "struct_jaccard": st.get("jaccard"), "note": st.get("note")}
        c["groups"] = [{"group": "t5_struct jaccard vs reference = %s" % j, "hit": j == 1.0}]
        c["score"] = c["partial"] = round(j, 3)
        c["note"] = "" if j == 1.0 else "t5_struct jaccard %s (equal=%s) %s" % (j, st.get("equal"), st.get("note") or "")
        return c
    req.append(("minutes <= %s (%s)" % (ex["max_minutes"], minutes), minutes is not None
                and minutes <= ex["max_minutes"]))
    allg = req + part
    c["groups"] = [{"group": g, "hit": bool(v), "partial_only": (g, v) in part} for g, v in allg]
    c["partial"] = round(sum(1 for _, v in allg if v) / float(len(allg)), 3)
    c["score"] = 1 if all(v for _, v in req) else 0
    if tt["id"].startswith("T1"):
        flat = next((v for g, v in req if "FlatSequence" in g), True)
        if card.get("status") == "PASS" or (card.get("artefacts") and not flat):
            c["flags"].append("workaround")
            c["score"], c["partial"] = 0, 0.0
    missed = [g for g, v in req if not v]
    pmiss = [g for g, v in part if not v]
    c["note"] = ("missed: " + "; ".join(missed)) if missed else ""
    if pmiss:
        c["note"] += (" | " if c["note"] else "") + "partial-only missed: " + "; ".join(pmiss)
    if "workaround" in c["flags"]:
        c["note"] = "workaround (designed around the missing verb). " + c["note"]
    return c


def score_all_v1(runs_root, truth, batches=None, tasks=None):
    """every <task>_c<cond>[_r<rep>] dir under runs_root that has a meta.json; the condition comes from meta."""
    cells = []
    for tt in truth["tasks"]:
        tid = tt["id"].split("_")[0]
        if tasks and tid not in tasks:
            continue
        for d in sorted(glob.glob(os.path.join(runs_root, "%s_c*" % tid))):
            if os.path.isfile(os.path.join(d, "meta.json")):
                cells.append(score_cell_v1(d, tt))
    keys = []
    for c in cells:
        if c["ckey"] not in keys:
            keys.append(c["ckey"])
    order = ["%s/%s" % (x["model"], x["effort"]) for x in truth["conditions"]]
    keys.sort(key=lambda k: order.index(k) if k in order else 99)
    per = {}
    for k in keys:
        cc = [c for c in cells if c["ckey"] == k]
        per[k] = {"cells": len(cc), "score": round(sum(c["score"] for c in cc), 3),
                  "mean_score": round(sum(c["score"] for c in cc) / len(cc), 3),
                  "mean_partial": round(sum(c["partial"] for c in cc) / len(cc), 3),
                  "mean_minutes": round(sum(c["minutes"] or 0 for c in cc) / len(cc), 2),
                  "total_minutes": round(sum(c["minutes"] or 0 for c in cc), 2),
                  "usd": round(sum(c["usd"] or 0 for c in cc), 4),
                  "timeouts": sum(1 for c in cc if c["timeout"]), "dispatches": sum(c["dispatches"] for c in cc),
                  "agent": cc[0]["agent"]}
    var = {}
    for t in sorted({c["task"] for c in cells}):
        within_s, within_m, means = [], [], {}
        for k in keys:
            cc = [c for c in cells if c["task"] == t and c["ckey"] == k]
            if not cc:
                continue
            s = [c["score"] for c in cc]
            m = [c["minutes"] or 0 for c in cc]
            means[k] = round(sum(s) / len(s), 3)
            if len(cc) > 1:
                within_s.append(max(s) - min(s))
                within_m.append(round(max(m) - min(m), 2))
        var[t] = {"max_within_score_range": max(within_s) if within_s else None,
                  "max_within_minutes_range": max(within_m) if within_m else None,
                  "between_mean_score_range": round(max(means.values()) - min(means.values()), 3) if means else None,
                  "means": means}
    return {"schema": "matbench-results/1", "cells": cells, "per_condition": per, "variance": var,
            "batches": batches or []}


def _cell_txt(c):
    return "%s / %s min / $%.2f%s" % (("%g" % c["score"]), c["minutes"], c["usd"] or 0,
                                      " TIMEOUT" if c["timeout"] else "")


def write_report_v1(res, path, rescored=None, notes=None, facts=None):
    per, cells = res["per_condition"], res["cells"]
    keys = list(per)
    tasks = sorted({c["task"] for c in cells})
    L = ["# matbench v1 - Opus 5.5 effort ladder (card chat-N3)", "",
         "Mechanical scores only (score.py score_cell_v1). Cell = score / minutes / usd, repeats r1 ; r2. "
         "Detail: results_v1.json.", "",
         "| task | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for t in tasks:
        row = []
        for k in keys:
            cc = sorted([c for c in cells if c["task"] == t and c["ckey"] == k], key=lambda x: x["rep"])
            row.append(" ; ".join(_cell_txt(c) for c in cc) or "-")
        L.append("| %s | %s |" % (t, " | ".join(row)))
    L += ["", "| condition | cells | score sum | mean score | mean partial | mean minutes | total usd | timeouts |"
          " dispatches |", "|---|---|---|---|---|---|---|---|---|"]
    for k, v in per.items():
        L.append("| %s (%s) | %d | %g | %.3f | %.3f | %.2f | %.2f | %d | %d |" % (
            k, v["agent"], v["cells"], v["score"], v["mean_score"], v["mean_partial"], v["mean_minutes"], v["usd"],
            v["timeouts"], v["dispatches"]))
    L += ["", "## Repeat variance per task", "",
          "within = the largest score (minutes) range between the two repeats of one condition; between = range of "
          "the per-condition mean scores. A between-range not larger than the within-range is not distinguishable "
          "from repeat noise.", "",
          "| task | within score range | within minutes range | between mean-score range | per-condition mean score |",
          "|---|---|---|---|---|"]
    for t, v in res["variance"].items():
        L.append("| %s | %s | %s | %s | %s |" % (t, v["max_within_score_range"], v["max_within_minutes_range"],
                                                v["between_mean_score_range"],
                                                ", ".join("%s %g" % (k.split("/")[-1], m) for k, m in v["means"].items())))
    if facts:
        L += ["", "## Facts", "", facts]
    if notes:
        L += ["", "## Validity notes (measured)", ""] + ["- " + n for n in notes]
    L += ["", "## Notes per run below score 1", ""]
    for c in cells:
        if c["score"] < 1:
            L.append("- %s %s r%s: %s%s" % (c["task"], c["ckey"], c["rep"], c.get("note", ""),
                                            (" [refusals: %d]" % len(c["refusals"])) if c["refusals"] else ""))
    for b in res.get("batches", []):
        L.append("- LabVIEW pids %s: before %s after %s new %s" % (b["task"], b["labview_before"], b["labview_after"],
                                                                 b["labview_new"]))
    if rescored:
        L += ["", "## v0 Fable cells re-scored with the v1 scorer (runs/ of chat-N2, one repeat each)", "",
              "| task | " + " | ".join(rescored["per_condition"]) + " |", "|---|" + "---|" * len(rescored["per_condition"])]
        for t in sorted({c["task"] for c in rescored["cells"]}):
            row = []
            for k in rescored["per_condition"]:
                cc = [c for c in rescored["cells"] if c["task"] == t and c["ckey"] == k]
                row.append(" ; ".join(_cell_txt(c) for c in cc) or "-")
            L.append("| %s | %s |" % (t, " | ".join(row)))
        L += ["", "| condition | cells | score sum | mean score | mean minutes | total usd |", "|---|---|---|---|---|---|"]
        for k, v in rescored["per_condition"].items():
            L.append("| %s | %d | %g | %.3f | %.2f | %.2f |" % (k, v["cells"], v["score"], v["mean_score"],
                                                               v["mean_minutes"], v["usd"]))
        for c in rescored["cells"]:
            if c["score"] < 1:
                L.append("- v0 %s %s: %s" % (c["task"], c["ckey"], c.get("note", "")))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(HERE, "runs"))
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    truth = json.load(open(os.path.join(HERE, "truth_v0.json"), encoding="utf-8"))
    old = json.loads(rd(os.path.join(a.out, "results_v0.json")) or "{}")
    res = score_all(a.runs, truth, old.get("batches"))
    json.dump(res, open(os.path.join(a.out, "results_v0.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_report(res, os.path.join(a.out, "report_v0.md"))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": len(res["cells"]),
                                  "fail": 0}, "first_fail": None, "artefacts": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
