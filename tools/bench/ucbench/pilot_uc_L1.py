r"""pilot_uc_L1 - card chat-B5: blind-score FIVE L1 answers (the pilot UC run + the four finished single-session
answers of the stopped B4 run) and write pilot_uc_L1.json / pilot_uc_L1.md. Facts only, no recommendation.

    py tools/bgrun.py --material --max-min 60 --log tools/bench/ucbench/pilot_score.log -- py -u tools/bench/ucbench/pilot_uc_L1.py

PREDICTION CONTRACT: results_pilot.json holds exactly 1 UC record for L1 (not invalid, answer non-empty); the four
answers runs/full/L1/{SH_r1,SH_r2,SXH_r1,SXH_r2}/answer.md exist; ucbench.score_all (one blind claude-opus-5-5/high
scorer cell per answer, arm hidden by an md5 label, par 5, fresh L1 worktree) returns a parsed blind JSON for all 5;
no new LabVIEW pid; no worktree left. RESULT line: gates = 5 scored answers + 2 hygiene checks.

WHAT EXISTED FIRST: ucbench.py (score_all, parse_stream, calls_summary, prepare), uc_score.py (metrics); reused, not
copied. New here: records for the four B4 answers rebuilt from their cell.log / full.log, token split main vs
sub-agent from the UC stream.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ucbench as UB  # noqa: E402

RUNS = os.path.join(HERE, "runs")
TK = ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens")


def stream_tokens(log):
    """usage summed over assistant events, split by parent_tool_use_id (None = main loop)."""
    out = {"main": dict.fromkeys(TK, 0), "sub": dict.fromkeys(TK, 0), "sub_events": 0}
    m = {"input_tokens": "inputTokens", "output_tokens": "outputTokens", "cache_read_input_tokens":
         "cacheReadInputTokens", "cache_creation_input_tokens": "cacheCreationInputTokens"}
    last, wf = {}, {}
    for ln in UB.MS.rd(log).splitlines():
        if '"subtype":"task_progress"' in ln[:60]:    # Workflow sub-agents: cumulative usage per task, last event wins
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            ag = [x for x in e.get("workflow_progress") or [] if x.get("type") == "workflow_agent"]
            wf[e.get("task_id")] = {"usage": e.get("usage"), "agents": len(ag),
                                    "agent_tokens_sum": sum(int(x.get("tokens") or 0) for x in ag),
                                    "agent_tool_calls_sum": sum(int(x.get("toolCalls") or 0) for x in ag),
                                    "phases": [x.get("title") for x in e.get("workflow_progress") or []
                                               if x.get("type") == "workflow_phase"]}
            out["workflow"] = wf
            continue
        if not ln.startswith('{"type":"assistant"'):
            continue
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        msg = e.get("message") or {}
        mid = msg.get("id")
        side = "sub" if e.get("parent_tool_use_id") else "main"
        per = {m[k]: v for k, v in (msg.get("usage") or {}).items() if k in m and isinstance(v, int)}
        old = last.get(mid, (side, {}))[1]    # one API message streams as several events: keep the max per field
        last[mid] = (side, {k: max(per.get(k, 0), old.get(k, 0)) for k in TK})
    for side, per in last.values():
        out["sub_events"] += side == "sub"
        for k in TK:
            out[side][k] += per[k]
    out["api_messages"] = len(last)
    return out


def old_record(arm, rep, full_log):
    d = os.path.join(RUNS, "full", "L1", "%s_r%d" % (arm, rep))
    text = UB.MS.rd(os.path.join(d, "c0", "cell.log"))
    env, _tools, uses, _e = UB.parse_stream(text)
    mu = env.get("modelUsage") or {}
    _, cs = UB.calls_summary(os.path.join(d, "c0", "calls.jsonl"))
    mt = re.search(r"ARM END L1 %s r%d usd ([\d.]+) min ([\d.]+)" % (arm, rep), full_log)
    return {"task": "L1", "arm": arm, "rep": rep, "source": "B4 runs/full", "answer": open(
        os.path.join(d, "answer.md"), encoding="utf-8").read(), "usd": float(env.get("total_cost_usd") or 0),
        "minutes": float(mt.group(2)) if mt else None, "turns": env.get("num_turns"), "top_tool_uses": uses,
        "calls": cs, "tokens": {k: sum(int(v.get(k) or 0) for v in mu.values()) for k in TK}}


def main():
    lv0 = UB.MB.labview_pids()
    doc, tasks = UB.load_tasks()
    res = json.load(open(os.path.join(HERE, "results_pilot.json"), encoding="utf-8"))
    uc = [r for r in res["records"] if r["arm"] == "UC" and r["task"] == "L1"]
    fails = []
    if len(uc) != 1 or uc[0].get("invalid") or not uc[0].get("answer"):
        fails.append("pilot UC record missing/invalid (%d)" % len(uc))
    recs = [dict(uc[0], source="pilot")] if uc and not fails else []
    if recs:
        recs[0]["stream_tokens"] = stream_tokens(os.path.join(RUNS, "pilot", "L1", "UC_r1", "c0", "cell.log"))
    full_log = UB.MS.rd(os.path.join(HERE, "full.log"))
    for arm, rep in (("SH", 1), ("SH", 2), ("SXH", 1), ("SXH", 2)):
        recs.append(old_record(arm, rep, full_log))
    score_usd = UB.score_all(doc, tasks, recs, os.path.join(RUNS, "pilot_score"), "", 60, 5)
    fails += ["%s r%d unscored" % (r["arm"], r["rep"]) for r in recs if not r.get("blind")]
    out = {"schema": "ucbench-pilot/1", "card": "chat-B5", "score_usd": round(score_usd, 3),
           "records": [{k: v for k, v in r.items() if k != "answer"} for r in recs]}
    art = os.path.join(HERE, "pilot_uc_L1.json")
    json.dump(out, open(art, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in recs:
        s = r.get("score") or {}
        UB.say("SCORE %s r%d label %s claims %s recall_blind %s recall_mech %s precision %s false %s extra_real %s "
               "usd %.2f min %s" % (r["arm"], r["rep"], r.get("scorer_label"), s.get("claims_n"), s.get("recall"),
                                    s.get("recall_mech"), s.get("precision"), s.get("false_claims"),
                                    s.get("extra_real"), r.get("usd") or 0, r.get("minutes")))
    UB.say("SCORER USD %.2f" % score_usd)
    leftwt = [w for w in UB.MB.git("worktree", "list").splitlines() if "/ucb/" in w.replace("\\", "/").lower()]
    new = sorted(set(UB.MB.labview_pids()) - set(lv0))
    fails += (["new LabVIEW pid %s" % new] if new else []) + (["worktrees left %s" % leftwt] if leftwt else [])
    for f in fails:
        UB.say("FAIL " + f)
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                                  "gates": {"pass": 7 - len(fails), "fail": len(fails)},
                                  "first_fail": fails[0] if fails else None,
                                  "artefacts": [{"path": UB.MS.rel(art), "md5": UB.MB.md5(art)}]}), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
