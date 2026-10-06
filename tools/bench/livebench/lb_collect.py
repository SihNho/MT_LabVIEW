# ---
# labview: none
# hardware: none
# ---
r"""lb_collect - livebench metrics collector (card chat-B7). Reads ONE finished arm run and writes ONE livebench/1 JSON.

Everything is read from files the run left behind, never from a session's summary:
  runner log      <wt>/tools/bench/cycle_runner.log      cycles, $ per cycle, ASSIGN / HANDBACK / JUDGE-LADDER / hooks
  envelopes       <wt>/tools/bench/*.log                 every `claude -p --output-format json` envelope (total_cost_usd,
                                                         session_id) - judgement, assignment, hand-back, any other cell
  peer archive    <wt>/archive/peer/*.md                 `**cost:** $x` (peer.ps1 cells: reviews, retrospective, facts)
  cards           <wt>/tools/bench/cards/task_*.json + result_*.json
  early catches   Claude transcripts of the arm (~/.claude/projects/<mangled worktree>/**/*.jsonl): guard_write's
                  `WRITE-CHECK` and every `BLOCKED by tools/hooks/guard_*.py`; plus guard_card.log REFUSE lines
  LabVIEW runs    bgrun logs whose launched script declares `# labview: read|build`; runner Error List hook runs
  saved VIs       the arm's claudeDev\bench\<arm> folder (md5 each)
  changes         `git diff --numstat <setup commit>` + untracked files in the worktree, by area
  containment     the sitecustomize write log (LIVEBENCH_WRITELOG) + lb_run's before/after snapshots (--snapshots)
The SAME schema serves any agent: a source that does not exist for an agent (e.g. Claude transcripts for a Codex arm)
is reported in `sources` as absent and its fields are null, never 0.
Usage: py tools/bench/livebench/lb_collect.py --worktree W --arm A --setup-commit SHA --t0 EPOCH [--t1 EPOCH]
       --claudedev-out DIR [--transcripts DIR] [--writelog F] [--snapshots F] [--flow purpose] [--agent claude-code] --out F
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

TS = r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)"
CYCLE_RE = re.compile(r"^CYCLE (\d+) \| " + TS + r" \| " + TS + r" \| exit (-?\d+) \| (\$[\d.]+|\?) \| (.*)$")
ASSIGN_END_RE = re.compile(r"^ASSIGN \| " + TS + r" \| cycle (\d+) round (\d+) \| end exit (-?\d+) \| (\$[\d.?]+) \| "
                           r"(\d+) min \| (\d+) card\(s\) \| (\w+)(?: \(([^)]*)\))? \| (.*)$")
HANDBACK_RE = re.compile(r"^HANDBACK \| " + TS + r" \| cycle (\d+) round (\d+) \| ([^|]+) \| ([^|]*) \|")
LADDER_END_RE = re.compile(r"^JUDGE-LADDER \| " + TS + r" \| cycle (\d+) end \| ([^|]+) \| (.*)$")
HOOK_RE = re.compile(r"^(ERRORLIST|MOTOR-LIMITS|LABVIEW-CLOSE) \| " + TS + r" \| cycle (\d+)[^|]*\| (.*)$")
STOP_RE = re.compile(r"^RUNNER STOP \| " + TS + r" \| (.*)$")
COST_RE = re.compile(r'"total_cost_usd"\s*:\s*([0-9.]+)')
SID_RE = re.compile(r'"session_id"\s*:\s*"([^"]+)"')
PEER_COST_RE = re.compile(r"\*\*cost:\*\*\s*\$([0-9.]+)")
BGRUN_START_RE = re.compile(r"^BGRUN START " + TS + r" limit [\d.]+ min: (.*)$", re.M)
SCRIPT_RE = re.compile(r"((?:tools[\\/])?[\w./\\-]+\.py)\b")
LVHDR_RE = re.compile(r"^# labview: (none|read|build)\s*$", re.M)
WRITECHECK_RE = re.compile(r"WRITE-CHECK \(tools/hooks/guard_write\.py[^)]*\) ([^:\\]+):(?:\\n|\s)+\s*(?:-\s*)?([^\\\"]{0,80})")
BLOCKED_RE = re.compile(r"BLOCKED by tools/hooks/(guard_\w+)\.py(?: \(([^)]{0,80})\))?")


def epoch(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def mangle(path):
    """Claude Code's project key for a cwd (every non-alphanumeric character -> '-')."""
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def fail_class(ff):
    if not ff:
        return None
    s = str(ff).strip()
    m = re.match(r"(GATE \S+|STOP:? \S+|X\d+\b|[A-Z][A-Z0-9_-]{2,}(?: [A-Z0-9_-]+)?)", s)
    return (m.group(1) if m else s[:40]).strip()


def runner_section(wt, t0, t1):
    out = {"cycles": {}, "stops": [], "hooks": []}
    for ln in read(os.path.join(wt, "tools", "bench", "cycle_runner.log")).splitlines():
        m = CYCLE_RE.match(ln)
        if m and t0 <= epoch(m.group(2)) <= t1:
            n = int(m.group(1))
            c = out["cycles"].setdefault(n, {"n": n})
            c.update({"start": m.group(2), "end": m.group(3), "exit": int(m.group(4)),
                      "wall_min": round((epoch(m.group(3)) - epoch(m.group(2))) / 60.0, 1),
                      "usd_runner": None if m.group(5) == "?" else float(m.group(5)[1:]), "next": m.group(6)[:200]})
            continue
        m = ASSIGN_END_RE.match(ln)
        if m and t0 <= epoch(m.group(1)) <= t1:
            c = out["cycles"].setdefault(int(m.group(2)), {"n": int(m.group(2))})
            c.setdefault("assign_rounds", []).append({
                "round": int(m.group(3)), "exit": int(m.group(4)), "usd": None if "?" in m.group(5) else float(m.group(5)[1:]),
                "minutes": int(m.group(6)), "cards": int(m.group(7)), "outcome": m.group(8), "trigger": m.group(9),
                "detail": m.group(10)[:200]})
            continue
        m = HANDBACK_RE.match(ln)
        if m and t0 <= epoch(m.group(1)) <= t1:
            c = out["cycles"].setdefault(int(m.group(2)), {"n": int(m.group(2))})
            c.setdefault("handbacks", []).append({"round": int(m.group(3)), "trigger": m.group(4).strip(),
                                                  "detail": m.group(5).strip()[:200]})
            continue
        m = LADDER_END_RE.match(ln)
        if m and t0 <= epoch(m.group(1)) <= t1:
            c = out["cycles"].setdefault(int(m.group(2)), {"n": int(m.group(2))})
            c["ladder"] = m.group(3).strip()
            c["delivered"] = m.group(4).strip().startswith("delivered")
            c["ladder_reason"] = m.group(4).strip()[:200]
            continue
        m = HOOK_RE.match(ln)
        if m and t0 <= epoch(m.group(2)) <= t1:
            out["hooks"].append({"hook": m.group(1), "cycle": int(m.group(3)), "text": m.group(4)[:160]})
            continue
        m = STOP_RE.match(ln)
        if m and t0 <= epoch(m.group(1)) <= t1:
            out["stops"].append(m.group(2)[:200])
    return out


def costs(wt, t0):
    sessions, peers = {}, []
    for p in glob.glob(os.path.join(wt, "tools", "bench", "*.log")):
        if os.path.getmtime(p) < t0:
            continue
        for ln in read(p).splitlines():
            m = COST_RE.search(ln)
            if not m:
                continue
            s = SID_RE.search(ln)
            key = s.group(1) if s else "%s:%s" % (os.path.basename(p), m.group(1))
            sessions[key] = {"usd": float(m.group(1)), "log": os.path.basename(p)}
    for p in glob.glob(os.path.join(wt, "archive", "peer", "*.md")):
        if os.path.getmtime(p) < t0:
            continue
        m = PEER_COST_RE.search(read(p))
        peers.append({"file": os.path.basename(p), "usd": float(m.group(1)) if m else None})
    s_usd = round(sum(v["usd"] for v in sessions.values()), 4)
    p_usd = round(sum(x["usd"] for x in peers if x["usd"] is not None), 4)
    return {"sessions_usd": s_usd, "peers_usd": p_usd, "total_usd": round(s_usd + p_usd, 4),
            "sessions": [dict(v, session=k) for k, v in sorted(sessions.items())], "peers": peers,
            "peers_without_cost": sum(1 for x in peers if x["usd"] is None)}


def cards(wt, t0):
    d = os.path.join(wt, "tools", "bench", "cards")
    out, statuses, classes = [], {}, {}
    for p in sorted(glob.glob(os.path.join(d, "task_*.json"))):
        if os.path.getmtime(p) < t0:
            continue
        cid = os.path.basename(p)[5:-5]
        try:
            task = json.load(open(p, encoding="utf-8"))
        except ValueError:
            task = {}
        rp = os.path.join(d, "result_%s.json" % cid)
        res = {}
        if os.path.exists(rp):
            try:
                res = json.load(open(rp, encoding="utf-8"))
            except ValueError:
                res = {"status": "INVALID"}
        st = res.get("status") or "NO-RESULT"
        statuses[st] = statuses.get(st, 0) + 1
        fc = fail_class(res.get("first_fail")) if st != "PASS" else None
        if fc:
            classes[fc] = classes.get(fc, 0) + 1
        out.append({"id": cid, "status": st, "first_fail": (str(res.get("first_fail"))[:200] if res.get("first_fail") else None),
                    "class": fc, "escalation": task.get("escalation"), "retry_of": task.get("retry_of_card"),
                    "labview": (task.get("flags") or {}).get("labview"),
                    "advances": list(task.get("advances") or []) + list(task.get("unblocks") or []),
                    "blocked_by": (res.get("blocked_by") or {}).get("device") if isinstance(res.get("blocked_by"), dict) else None})
    return {"issued": len(out), "by_status": statuses, "first_fail_classes": classes,
            "retries": sum(1 for c in out if c["retry_of"]), "escalations": sum(1 for c in out if c["escalation"]),
            "list": out}


def early_catches(wt, t0, tdir):
    res = {"guard_write": {"count": 0, "classes": {}}, "launch_gates": {"count": 0, "classes": {}},
           "guard_card": {"count": 0, "classes": {}}, "transcripts_read": 0}
    seen = set()
    if tdir and os.path.isdir(tdir):
        for p in glob.glob(os.path.join(tdir, "**", "*.jsonl"), recursive=True):
            if os.path.getmtime(p) < t0:
                continue
            res["transcripts_read"] += 1
            for i, ln in enumerate(read(p).splitlines()):
                try:
                    uid = json.loads(ln).get("uuid") or "%s:%d" % (p, i)
                except ValueError:
                    uid = "%s:%d" % (p, i)
                for m in WRITECHECK_RE.finditer(ln):
                    k = (uid, "w", m.group(1))
                    if k in seen:
                        continue
                    seen.add(k)
                    cls = re.sub(r"[^a-z ]", "", m.group(2).lower()).strip()[:40] or "?"
                    res["guard_write"]["count"] += 1
                    res["guard_write"]["classes"][cls] = res["guard_write"]["classes"].get(cls, 0) + 1
                for m in BLOCKED_RE.finditer(ln):
                    k = (uid, "b", m.group(0))
                    if k in seen:
                        continue
                    seen.add(k)
                    cls = m.group(1) + (" (%s)" % m.group(2) if m.group(2) else "")
                    res["launch_gates"]["count"] += 1
                    res["launch_gates"]["classes"][cls[:90]] = res["launch_gates"]["classes"].get(cls[:90], 0) + 1
    else:
        res["transcripts_read"] = None
    for ln in read(os.path.join(wt, "tools", "bench", "cards", "guard_card.log")).splitlines():
        m = re.match(TS + r" \| REFUSE \S+ \S+ \| (.*)$", ln)
        if m and epoch(m.group(1)) >= t0:
            cls = re.sub(r"^CARD \S+ \([^)]*\): ", "", m.group(2))[:60]
            res["guard_card"]["count"] += 1
            res["guard_card"]["classes"][cls] = res["guard_card"]["classes"].get(cls, 0) + 1
    return res


def labview_runs(wt, t0, runner):
    runs = []
    for p in glob.glob(os.path.join(wt, "tools", "bench", "*.log")):
        if os.path.getmtime(p) < t0:
            continue
        for m in BGRUN_START_RE.finditer(read(p)):
            if epoch(m.group(1)) < t0:
                continue
            cmd = m.group(2)
            lv = None
            for s in SCRIPT_RE.findall(cmd):
                sp = s if os.path.isabs(s) else os.path.join(wt, s)
                h = LVHDR_RE.search(read(sp)) if os.path.isfile(sp) else None
                if h:
                    lv = h.group(1)
                    break
            if lv in ("read", "build"):
                runs.append({"log": os.path.basename(p), "start": m.group(1), "labview": lv, "cmd": cmd[:160]})
    hook_runs = [h for h in runner["hooks"] if h["hook"] == "ERRORLIST" and "REUSE" not in h["text"]]
    return {"count": len(runs), "hook_errorlist_runs": len(hook_runs), "runs": sorted(runs, key=lambda r: r["start"])}


def saved_vis(out_dir, start_vi):
    res = []
    if out_dir and os.path.isdir(out_dir):
        for p in sorted(glob.glob(os.path.join(out_dir, "**", "*.vi"), recursive=True)):
            res.append({"path": p, "md5": md5(p), "bytes": os.path.getsize(p),
                        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
                        "start_copy": os.path.basename(p) == (start_vi or {}).get("name") and md5(p) == (start_vi or {}).get("md5")})
    return res


def area(path):
    p = path.replace("\\", "/")
    if p.startswith("tools/bench/"):
        return "tools/bench"
    if p.startswith("tools/recipes/"):
        return "tools/recipes"
    if p.startswith("tools/hooks/"):
        return "tools/hooks"
    if p.startswith("tools/"):
        return "tools"
    for a in ("docs/", "archive/", ".claude/", ".livebench/"):
        if p.startswith(a):
            return a[:-1]
    return p if "/" not in p else "other"


def git(wt, *args):
    r = subprocess.run(["git", "-C", wt] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def changes(wt, base):
    by, files, add, dele, created = {}, 0, 0, 0, []
    status = {}
    for ln in git(wt, "diff", "--name-status", base).splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2:
            status[parts[-1]] = parts[0][0]
    for ln in git(wt, "diff", "--numstat", base).splitlines():
        parts = ln.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        a, d = (int(a) if a.isdigit() else 0), (int(d) if d.isdigit() else 0)
        files, add, dele = files + 1, add + a, dele + d
        b = by.setdefault(area(path), {"files": 0, "added": 0, "deleted": 0})
        b["files"], b["added"], b["deleted"] = b["files"] + 1, b["added"] + a, b["deleted"] + d
        if status.get(path) == "A":
            created.append(path)
    for path in git(wt, "ls-files", "--others", "--exclude-standard").splitlines():
        n = len(read(os.path.join(wt, path)).splitlines())
        files, add = files + 1, add + n
        b = by.setdefault(area(path), {"files": 0, "added": 0, "deleted": 0})
        b["files"], b["added"] = b["files"] + 1, b["added"] + n
        created.append(path)
    tools_new = sorted(p for p in created if area(p) in ("tools", "tools/hooks") and p.endswith((".py", ".ps1")))
    recipes_new = sorted(p for p in created if area(p) == "tools/recipes")
    return {"files": files, "lines_added": add, "lines_deleted": dele, "by_area": by,
            "tools_created": tools_new, "recipes_created": recipes_new,
            "head": git(wt, "rev-parse", "HEAD").strip(), "base": base}


def adoptions(wt, t0):
    out = []
    for ln in read(os.path.join(wt, "tools", "bench", "adopted_scratch.jsonl")).splitlines():
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if float(r.get("t") or 0) >= t0:
            out.append({"stage": r.get("stage"), "artefact": (r.get("artefact") or {}).get("path"),
                        "md5": (r.get("artefact") or {}).get("md5"), "iso": r.get("iso"), "plan_md5s": r.get("plan_md5s"),
                        "gates": r.get("gates"), "required": r.get("required"), "log": r.get("log")})
    return out


NEXT_RE = re.compile(r"^NEXT \| " + TS + r" \| cycle (\d+) \| [^|]* \| act: (.*?) \| (?:advances|unblocks): (.*)$")


def _ids(text):
    return re.findall(r"\b(R\d+(?:\.\d+)?|M\d+)\b", str(text))


def goalmap(text):
    try:
        g = json.loads(text)
    except ValueError:
        return None
    st = {x["id"]: x.get("status") for x in (g.get("requirements") or []) + (g.get("milestones") or []) if x.get("id")}
    return {"status": st, "current": g.get("current")}


def plan_progress(wt, setup, t0, t1, cyc, card_list, adopts, cfg):
    """PRIMARY metric (user 2026-10-06): whole-project progress on docs/goalmap.json. Per cycle: the purpose it worked on
    (assign cards / NEXT line, with its goal ids), the PASS / non-PASS cards per goal id, re-plans (a cycle whose goal ids
    differ from the previous one's), goal-map status changes start -> end, the critical-path position, and the M3 detail
    (ring P4 ops/sessions adopted, ring steps adopted, each adoption's gates)."""
    g0 = goalmap(git(wt, "show", "%s:docs/goalmap.json" % setup))
    g1 = goalmap(read(os.path.join(wt, "docs", "goalmap.json")))
    changes_ = []
    if g0 and g1:
        for k in sorted(set(g0["status"]) | set(g1["status"])):
            if g0["status"].get(k) != g1["status"].get(k):
                changes_.append({"id": k, "from": g0["status"].get(k), "to": g1["status"].get(k)})
    nexts = {}
    for ln in read(os.path.join(wt, "tools", "bench", "cycle_runner.log")).splitlines():
        m = NEXT_RE.match(ln)
        if m and t0 <= epoch(m.group(1)) <= t1:
            nexts[int(m.group(2))] = {"act": m.group(3)[:160], "ids": _ids(m.group(4))}
    per, prev = [], None
    start_next = None
    try:
        start_next = json.loads(git(wt, "show", "%s:tools/bench/next.json" % setup))
    except ValueError:
        pass
    prev = sorted(set(_ids(json.dumps((start_next or {}).get("advances") or (start_next or {}).get("unblocks") or []))))
    replans = []
    for c in cyc:
        n = c["n"]
        purposes = []
        for p in sorted(glob.glob(os.path.join(wt, "tools", "bench", "cards", "assign_%d_*.json" % n))):
            try:
                pu = json.load(open(p, encoding="utf-8")).get("purpose") or {}
            except ValueError:
                continue
            purposes.append({"act": str(pu.get("act"))[:160],
                             "ids": sorted(set(_ids(json.dumps(pu.get("advances") or []) + json.dumps(pu.get("unblocks") or []))))})
        ids = sorted(set(i for p in purposes for i in p["ids"])) or (nexts.get(n) or {}).get("ids") or []
        if prev is not None and ids and sorted(set(ids)) != prev:
            replans.append({"cycle": n, "from": prev, "to": sorted(set(ids))})
        prev = sorted(set(ids)) if ids else prev
        per.append({"cycle": n, "purposes": purposes, "next_after": nexts.get(n), "goal_ids": ids,
                    "purpose_met": c.get("purpose_met"), "delivered": c.get("delivered")})
    by_goal = {}
    for cd in card_list:
        for gid in sorted(set(_ids(json.dumps(cd.get("advances") or [])))):
            b = by_goal.setdefault(gid, {"PASS": 0, "other": 0, "cards": []})
            b["PASS" if cd["status"] == "PASS" else "other"] += 1
            b["cards"].append("%s:%s" % (cd["id"], cd["status"]))
    crit = []
    for mid in cfg.get("critical_path") or []:
        crit.append({"id": mid, "start": (g0 or {}).get("status", {}).get(mid), "end": (g1 or {}).get("status", {}).get(mid),
                     "pass_cards": (by_goal.get(mid) or {}).get("PASS", 0)})
    nxt = next((x["id"] for x in crit if x["end"] != "done"), None)
    m3 = cfg.get("m3_detail") or {}
    sre = re.compile(m3.get("stage_re") or r"ring_(p\d+)(?:_s(\d+))?", re.I)
    base = m3.get("baseline") or {}
    ops, sess, steps, ad = base.get("ops_adopted", 0), base.get("sessions_adopted", 0), {}, []
    for a_ in adopts:
        m = sre.search(str(a_.get("stage") or ""))
        step = m.group(1).upper() if m else None
        n_act = 0
        for pp in (a_.get("plan_md5s") or {}):
            try:
                n_act += len(json.load(open(os.path.join(wt, pp), encoding="utf-8")).get("actions") or [])
            except (OSError, ValueError):
                pass
        if step == "P4" and m.group(2):
            ops, sess = ops + n_act, sess + 1
        if step:
            steps[step] = steps.get(step, 0) + 1
        ad.append(dict(a_, step=step, plan_actions=n_act))
    return {"goalmap_changes": changes_, "goalmap_current": {"start": (g0 or {}).get("current"), "end": (g1 or {}).get("current")},
            "goalmap_changed": bool(changes_) or ((g0 or {}).get("current") != (g1 or {}).get("current")),
            "per_cycle": per, "replans": replans, "cards_by_goal": by_goal,
            "critical_path": crit, "next_open_milestone": nxt,
            "m3_detail": {"p4_ops_adopted": ops, "p4_ops_total": m3.get("p4_total_ops"),
                          "p4_sessions_adopted": sess, "p4_sessions_total": m3.get("p4_sessions"),
                          "ring_step_adoptions": steps, "adoptions": ad,
                          "plan_files_changed": [ln for ln in git(wt, "diff", "--numstat", setup, "--", "tools/bench/plan_*.json",
                                                                  "docs/d1", "docs/goalmap.json").splitlines()]}}


def containment(writelog, snapshots, t0):
    res = {"writes_by_class": {}, "refused": [], "writelog": writelog, "snapshots": None}
    for ln in read(writelog).splitlines() if writelog else []:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        res["writes_by_class"][r["class"]] = res["writes_by_class"].get(r["class"], 0) + 1
        if r.get("refused"):
            res["refused"].append({"path": r["path"], "class": r["class"], "argv0": r.get("argv0"), "t": r.get("t")})
    if snapshots and os.path.exists(snapshots):
        res["snapshots"] = json.load(open(snapshots, encoding="utf-8"))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--setup-commit", required=True)
    ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--claudedev-out", default="")
    ap.add_argument("--transcripts", default=None, help="default ~/.claude/projects/<mangled worktree>")
    ap.add_argument("--writelog", default="")
    ap.add_argument("--snapshots", default="")
    ap.add_argument("--flow", default="purpose")
    ap.add_argument("--agent", default="claude-code")
    ap.add_argument("--extras", default="")
    ap.add_argument("--start-vi", default="", help="json {name, md5}")
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--arms", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "arms.json"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    wt = os.path.abspath(a.worktree)
    t1 = a.t1 or time.time()
    tdir = a.transcripts if a.transcripts is not None else os.path.join(
        os.path.expanduser("~"), ".claude", "projects", mangle(wt))
    start_vi = json.loads(a.start_vi) if a.start_vi else None
    run = runner_section(wt, a.t0, t1)
    cyc = [run["cycles"][k] for k in sorted(run["cycles"])]
    for c in cyc:
        rounds = c.get("assign_rounds") or []
        c["purpose_met"] = (any(r["outcome"] == "PURPOSE_MET" for r in rounds) if rounds else
                            (None if a.flow == "legacy" else False))
    hb = [dict(h, cycle=c["n"]) for c in cyc for h in c.get("handbacks") or []]
    trig = {}
    for h in hb:
        trig[h["trigger"]] = trig.get(h["trigger"], 0) + 1
    cfg = (json.load(open(a.arms, encoding="utf-8")).get("progress") or {}) if os.path.exists(a.arms) else {}
    adopts, card_rec = adoptions(wt, a.t0), cards(wt, a.t0)
    rec = {"schema": "livebench/1", "arm": a.arm, "agent": a.agent, "flow": a.flow,
           "extras": [x for x in a.extras.split(",") if x], "stub": a.stub,
           "window": {"t0": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(a.t0)),
                      "t1": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t1)),
                      "wall_min": round((t1 - a.t0) / 60.0, 1)},
           "plan_progress": plan_progress(wt, a.setup_commit, a.t0, t1, cyc, card_rec["list"], adopts, cfg),
           "secondary": "every key below plan_progress is a secondary metric (user 2026-10-06)",
           "cycles": cyc,
           "purpose_met_cycles": sum(1 for c in cyc if c.get("purpose_met")),
           "delivered_cycles": sum(1 for c in cyc if c.get("delivered")),
           "adoptions": adopts,
           "runner_stops": run["stops"], "runner_hooks": run["hooks"],
           "usd": costs(wt, a.t0),
           "cards": card_rec,
           "early_catches": early_catches(wt, a.t0, tdir),
           "handbacks": {"count": len(hb), "triggers": trig, "list": hb},
           "labview_runs": labview_runs(wt, a.t0, run),
           "saved_vis": saved_vis(a.claudedev_out, start_vi),
           "changes_outside_claudedev": changes(wt, a.setup_commit),
           "containment": containment(a.writelog, a.snapshots, a.t0),
           "sources": {"runner_log": os.path.exists(os.path.join(wt, "tools", "bench", "cycle_runner.log")),
                       "transcripts": tdir if os.path.isdir(tdir or "") else None,
                       "writelog": bool(a.writelog and os.path.exists(a.writelog)),
                       "snapshots": bool(a.snapshots and os.path.exists(a.snapshots))}}
    rec["changes_outside_claudedev"]["tools_created_count"] = len(rec["changes_outside_claudedev"]["tools_created"])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    pp = rec["plan_progress"]
    print("LB-COLLECT %s -> %s | PROGRESS goalmap changes %d, next open %s, replans %d, P4 ops %s/%s sessions %s/%s | "
          "cycles %d purpose_met %d | $%.2f | cards %d %s | catches w%d g%d c%d | lv %d | vis %d"
          % (a.arm, a.out, len(pp["goalmap_changes"]), pp["next_open_milestone"], len(pp["replans"]),
             pp["m3_detail"]["p4_ops_adopted"], pp["m3_detail"]["p4_ops_total"], pp["m3_detail"]["p4_sessions_adopted"],
             pp["m3_detail"]["p4_sessions_total"],
             len(cyc), rec["purpose_met_cycles"], rec["usd"]["total_usd"], rec["cards"]["issued"],
             json.dumps(rec["cards"]["by_status"]), rec["early_catches"]["guard_write"]["count"],
             rec["early_catches"]["launch_gates"]["count"], rec["early_catches"]["guard_card"]["count"],
             rec["labview_runs"]["count"], len(rec["saved_vis"])), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
