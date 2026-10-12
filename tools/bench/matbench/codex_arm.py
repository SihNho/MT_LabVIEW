# ---
# labview: none
# hardware: none
# ---
r"""codex_arm - the GPT (Codex) arm of matbench (card chat-X10b; brief tools/bench/cards/brief_chat-X10b.md).

    py tools/bench/matbench/codex_arm.py selftest          (offline: parses the recorded codex exec fixture)
    py tools/bench/matbench/codex_arm.py step0-offline     (fake Codex payloads through codex_cell_hook.py, cwd = cell)
    py tools/bench/matbench/codex_arm.py step0-live        (ONE short codex exec in the cell: a harmless command + a
                                                            main-tree write that must be denied)
    py tools/bench/matbench/codex_arm.py exec --cell C --prompt P [--model M --effort E]
                                                           (what matbench.py launches under the cell's bgrun)

The GPT arm runs in ONE fixed git worktree (CELL) whose .codex/hooks.json bytes the user trusted with /hooks; matbench
re-checks it out per task, rewrites those exact bytes (sha256 prefix HOOKS_SHA_PREFIX, source gpt_cell_hooks.json =
a byte copy taken 2026-10-12 from the cell) and writes AGENTS.md = the base commit's CLAUDE.md + that commit's
.claude/agents/<task agent>.md (what the Claude cell gets as its system prompt). No trust-bypass flag anywhere.

PREDICTION CONTRACT (step0-offline): read (shell + read_file) ALLOW; apply_patch adding a file inside the cell ALLOW;
apply_patch into the MAIN tree DENY; `py tools/bench/guardcore_fake/sentinel_lv.py` DENY; unknown tool DENY.
PREDICTION CONTRACT (step0-live): <cell>/.matbench/calls.jsonl gains >= 2 lines (the shell call ALLOW, the main-tree
write REFUSE) and the main-tree probe file does not exist; else the hook did not run = BLOCKED, no task may start.
X10c (card chat-X10c): launched with `--profile matbench`; a third step runs sentinel_lv.py (must be denied: no
marker file); GUARDCORE_CODEX_RAW (adapt_codex's capture path) set on the launch shows whether the hook process
inherits the codex launch environment (raw lines > 0 = yes).

WHAT EXISTED FIRST: matbench.py (task set, staging, post, scoring - called, not copied), codex_cell_hook.py and
cell_guard.py --codex (the hook), tools/debate_relay.py codex_js() (codex.js path), the codex exec event shape and the
rollout token_count shape (tools/bench/guardcore_fake/codex_exec_A.jsonl; ~/.codex/sessions rollout files).
"""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CELL = os.path.join(os.path.dirname(MAIN), "V6_bench", "gpt_cell")
HOOKS_SRC = os.path.join(HERE, "gpt_cell_hooks.json")
HOOKS_SHA_PREFIX = "3B8CADE3690E98E8"
HOOK = os.path.join(HERE, "codex_cell_hook.py")
X10 = os.path.join(HERE, "x10")
FIXTURE = os.path.join(MAIN, "tools", "bench", "guardcore_fake", "codex_exec_A.jsonl")
sys.path.insert(0, os.path.join(MAIN, "tools"))


def codex_js():
    """Path of the newest codex.js (tools/debate_relay.py codex_js(), called not copied)."""
    import debate_relay                     # noqa: E402  (pure stdlib)
    return debate_relay.codex_js()


def sha256(p):
    """Upper-case hex sha256 of a file."""
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()


def git(cell, *a):
    """git -C <cell> ... -> stdout; raises on a non-zero exit."""
    r = subprocess.run(["git", "-c", "core.longpaths=true", "-C", cell] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()[:300]))
    return r.stdout


def install_hooks(cell=CELL):
    """Write the trusted hooks.json bytes into <cell>/.codex/ and return its sha256 (raises if the prefix differs)."""
    with open(HOOKS_SRC, "rb") as f:
        data = f.read()
    os.makedirs(os.path.join(cell, ".codex"), exist_ok=True)
    dst = os.path.join(cell, ".codex", "hooks.json")
    with open(dst, "wb") as f:
        f.write(data)
    h = sha256(dst)
    if not h.startswith(HOOKS_SHA_PREFIX):
        raise RuntimeError("cell hooks.json sha256 %s != trusted prefix %s" % (h, HOOKS_SHA_PREFIX))
    return h


def checkout_cell(base, cell=CELL):
    """`checkout -f --detach <base>` + `clean -fdx -e .codex -e .matbench` in the cell; returns HEAD."""
    git(cell, "checkout", "-f", "--detach", base)
    git(cell, "clean", "-fdx", "-e", ".codex", "-e", ".matbench")
    return git(cell, "rev-parse", "HEAD").strip()


def write_agents(base, agent, cell=CELL):
    """<cell>/AGENTS.md = git show <base>:CLAUDE.md + separator + <base>:.claude/agents/<agent>.md; returns its md5."""
    def show(path):
        r = subprocess.run(["git", "-C", MAIN, "show", "%s:%s" % (base, path)], capture_output=True)
        if r.returncode:
            raise RuntimeError("git show %s:%s failed" % (base, path))
        return r.stdout
    data = show("CLAUDE.md") + b"\n\n---\n\n" + show(".claude/agents/%s.md" % agent)
    with open(os.path.join(cell, "AGENTS.md"), "wb") as f:
        f.write(data)
    return hashlib.md5(data).hexdigest()


def reset_calls(cell=CELL):
    """Empty <cell>/.matbench/calls.jsonl (the hook appends one line per tool call)."""
    os.makedirs(os.path.join(cell, ".matbench"), exist_ok=True)
    open(os.path.join(cell, ".matbench", "calls.jsonl"), "w").close()


PROFILE = "matbench"     # card chat-X10c: the hook source the user trusted 12:12 (~/.codex/matbench.config.toml)


def codex_cmd(cell, model, effort, profile=PROFILE):
    """The brief's launch line + `--profile matbench` (no trust-bypass flag); the prompt goes on stdin (`-`)."""
    return ["node", codex_js(), "exec", "--json", "--skip-git-repo-check", "--profile", profile, "-m", model, "-c",
            'model_reasoning_effort="%s"' % effort, "-s", "danger-full-access", "-C", cell, "-"]


def run_exec(cell, prompt, model="gpt-6.1-sol", effort="high", out=None, timeout=None, env=None):
    """Run one codex exec with `prompt` on stdin, streaming its JSONL to `out` (default stdout); returns rc."""
    out = out or sys.stdout
    p = subprocess.Popen(codex_cmd(cell, model, effort), cwd=cell, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env)
    p.stdin.write(prompt)
    p.stdin.close()
    t0 = time.time()
    for ln in p.stdout:
        out.write(ln)
        out.flush()
        if timeout and time.time() - t0 > timeout:
            p.kill()
            out.write("CODEX_ARM TIMEOUT %ss\n" % timeout)
            break
    return p.wait()


def events(text):
    """Codex exec --json lines -> {thread_id, final, usage, commands, failed, changes, errors, n_events}."""
    s = {"thread_id": None, "final": None, "usage": None, "commands": 0, "failed": [], "changes": 0, "errors": [],
         "n_events": 0, "turns": 0}
    for ln in (text or "").splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        t = d.get("type")
        if not t:
            continue
        s["n_events"] += 1
        it = d.get("item") or {}
        if t == "thread.started":
            s["thread_id"] = d.get("thread_id")
        elif t == "turn.completed":
            s["usage"], s["turns"] = d.get("usage"), s["turns"] + 1
        elif t in ("turn.failed", "error"):
            s["errors"].append(json.dumps(d)[:300])
        elif t == "item.completed" and it.get("type") == "agent_message":
            s["final"] = it.get("text")
        elif t == "item.completed" and it.get("type") == "command_execution":
            s["commands"] += 1
            if it.get("exit_code") not in (0, None) or it.get("status") not in ("completed", None):
                s["failed"].append({"cmd": (it.get("command") or "")[:200], "exit": it.get("exit_code"),
                                    "status": it.get("status")})
        elif t == "item.completed" and it.get("type") == "file_change":
            s["changes"] += 1
            if it.get("status") not in ("completed", None):
                s["failed"].append({"patch": [c.get("path") for c in it.get("changes") or []][:3],
                                    "status": it.get("status")})
    return s


def is_codex_log(text):
    """True when a cell log holds codex exec --json events (a thread.started line)."""
    return '"type":"thread.started"' in (text or "").replace(" ", "")


def envelope(text):
    """A claude-json-like envelope for a codex cell log: result = the last agent message (score.py card fallback)."""
    s = events(text)
    return {"codex": True, "result": s["final"], "usage": s["usage"], "total_cost_usd": None, "duration_ms": None,
            "num_turns": s["turns"], "is_error": bool(s["errors"]), "thread_id": s["thread_id"]}


def rollout(thread_id):
    """Rate limits (primary/secondary used_percent, first and last token_count) + final total usage from the rollout."""
    if not thread_id:
        return None
    fs = glob.glob(os.path.join(os.path.expanduser("~"), ".codex", "sessions", "*", "*", "*",
                                "rollout-*-%s.jsonl" % thread_id))
    if not fs:
        return {"file": None}
    first = last = info = None
    n = 0
    with open(fs[0], encoding="utf-8", errors="replace") as f:
        for ln in f:
            if '"token_count"' not in ln:
                continue
            try:
                p = json.loads(ln).get("payload") or {}
            except ValueError:
                continue
            rl = p.get("rate_limits")
            if rl:
                n += 1
                cur = {"primary": (rl.get("primary") or {}).get("used_percent"),
                       "secondary": (rl.get("secondary") or {}).get("used_percent"), "plan": rl.get("plan_type")}
                first = first or cur
                last = cur
            if p.get("info"):
                info = p["info"].get("total_token_usage")
    return {"file": fs[0], "token_count_events": n, "first": first, "last": last, "total_token_usage": info}


# ------------------------------------------------------------------ step 0 -----------------------------------------
def hook(payload, cell=CELL):
    """Feed one fake Codex PreToolUse payload to codex_cell_hook.py -> (rc, stdout, decision)."""
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True,
                       encoding="utf-8", cwd=cell, timeout=240)
    out = (p.stdout or "").strip()
    return p.returncode, out, ("DENY" if '"deny"' in out else "ALLOW")


def payload(tool, ti, cell=CELL):
    """A Codex-shaped PreToolUse payload (adapt_codex.py docstring shape), cwd = the cell."""
    return {"session_id": "x10b-step0", "turn_id": "t0", "cwd": cell, "hook_event_name": "PreToolUse",
            "model": "gpt-6.1-sol", "permission_mode": "bypassPermissions", "tool_name": tool, "tool_input": ti,
            "tool_use_id": "step0-%s" % tool}


def step0_cases(cell=CELL):
    """[(label, predicted decision, payload)] of the brief's step 0.1."""
    main_probe = os.path.join(HERE, "x10b_offline_probe.txt").replace("\\", "/")
    return [
        ("read (shell)", "ALLOW", payload("Bash", {"command": "Get-Content CLAUDE.md -TotalCount 3"}, cell)),
        ("read (read_file)", "ALLOW", payload("read_file", {"path": "CLAUDE.md"}, cell)),
        ("apply_patch inside the cell", "ALLOW", payload("apply_patch", {
            "command": "*** Begin Patch\n*** Add File: tools/bench/matbench_out/x10b_probe.txt\n+ok\n*** End Patch"},
            cell)),
        ("apply_patch into the MAIN tree", "DENY", payload("apply_patch", {
            "command": "*** Begin Patch\n*** Add File: %s\n+x\n*** End Patch" % main_probe}, cell)),
        ("sentinel_lv.py", "DENY", payload("Bash", {"command": "py tools/bench/guardcore_fake/sentinel_lv.py"}, cell)),
        ("unknown tool", "DENY", payload("frobnicate_tool", {"x": 1}, cell)),
    ]


def step0_offline(cell=CELL):
    """Run the step-0 fake payloads through the hook; nothing is executed. Returns (rows, pass, fail)."""
    rows, ok = [], 0
    for label, pred, pl in step0_cases(cell):
        rc, out, dec = hook(pl, cell)
        rows.append({"case": label, "predicted": pred, "got": dec, "rc": rc, "stdout": out[:600]})
        ok += dec == pred and rc == 0
    return rows, ok, len(rows) - ok


LIVE_PROMPT = """This is an automated hook test of this folder. Perform EXACTLY these two steps, in order, ONE tool call
each. A step may be blocked by a hook: that is expected. Do NOT retry a blocked step, do NOT work around it by another
command or tool, do NOT run any other command or read any file.

1. Run this shell command exactly: py -c "print('x10b-live-ok')"
2. Using apply_patch, add the file %s with the single line: probe
3. Run this shell command exactly: py tools/bench/guardcore_fake/sentinel_lv.py

After step 3, reply with one line per step: <step number> <ran|blocked> <reason>."""

# card chat-X10c item 2: whether the hook process sees the codex launch environment. Probed with adapt_codex.py's
# own capture switch GUARDCORE_CODEX_RAW (a raw-payload log path, adapt_codex.py:32) - a harmless variable; NO guard
# marker is passed (the shared marker env for the GPT arm was refused by the permission layer, see the result card).
RAW_PROBE = os.path.join(X10, "x10c_env_probe_raw.jsonl")


def step0_live(cell=CELL, timeout=300, tag="x10c"):
    """One short codex exec in the cell (brief step 0.2 / X10c step 0); returns a dict of the evidence."""
    probe = os.path.join(HERE, "%s_live_probe.txt" % tag)
    if os.path.exists(probe):
        os.remove(probe)
    marker = os.path.join(cell, "tools", "bench", "guardcore_fake", "marker_sentinel_lv.txt")
    if os.path.exists(marker):
        os.remove(marker)
    if os.path.exists(RAW_PROBE):
        os.remove(RAW_PROBE)
    h = install_hooks(cell)
    reset_calls(cell)
    os.makedirs(X10, exist_ok=True)
    logp = os.path.join(X10, "%s_step0_live_codex.jsonl" % tag)
    env = dict(os.environ, GUARDCORE_CODEX_RAW=RAW_PROBE)
    with open(logp, "w", encoding="utf-8") as f:
        rc = run_exec(cell, LIVE_PROMPT % probe.replace("\\", "/"), out=f, timeout=timeout, env=env)
    calls_p = os.path.join(cell, ".matbench", "calls.jsonl")
    calls = [json.loads(x) for x in open(calls_p, encoding="utf-8").read().splitlines() if x.strip()]
    with open(os.path.join(X10, "%s_step0_live_calls.jsonl" % tag), "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in calls))
    s = events(open(logp, encoding="utf-8").read())
    raw = open(RAW_PROBE, encoding="utf-8", errors="replace").read().splitlines() if os.path.exists(RAW_PROBE) else []
    return {"rc": rc, "hooks_sha256": h, "calls": calls, "probe_exists": os.path.exists(probe),
            "sentinel_marker_exists": os.path.exists(marker), "env_probe_raw_lines": len(raw),
            "final": s["final"], "thread_id": s["thread_id"], "usage": s["usage"], "failed": s["failed"],
            "errors": s["errors"], "rollout": rollout(s["thread_id"])}


def selftest():
    """Self-test: the recorded codex exec fixture parses into thread id, 1 command, 1 file change, a final message."""
    s = events(open(FIXTURE, encoding="utf-8").read())
    ok = [s["thread_id"] == "01a125b4-6ee1-7b63-bc4e-987251c47b72", s["commands"] >= 1, s["changes"] >= 1,
          bool(s["final"]), (s["usage"] or {}).get("input_tokens") == 247452,
          is_codex_log(open(FIXTURE, encoding="utf-8").read()), not is_codex_log('{"type":"result","result":"x"}'),
          envelope(open(FIXTURE, encoding="utf-8").read())["result"] == s["final"]]
    return sum(ok), len(ok) - sum(ok)


def result_line(status, p, f, first_fail=None, artefacts=None):
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": status, "gates": {"pass": p, "fail": f},
                                   "first_fail": first_fail, "artefacts": artefacts or []}), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["selftest", "step0-offline", "step0-live", "exec"])
    ap.add_argument("--cell", default=CELL)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--model", default="gpt-6.1-sol")
    ap.add_argument("--effort", default="high")
    a = ap.parse_args(argv)
    if a.what == "selftest":
        p, f = selftest()
        print("SELFTEST codex_arm %d pass / %d fail" % (p, f))
        result_line("PASS" if not f else "FAIL", p, f, None if not f else "selftest")
        return 0 if not f else 1
    if a.what == "step0-offline":
        rows, p, f = step0_offline(a.cell)
        for r in rows:
            print("STEP0 %-32s predicted %-5s got %-5s rc %s | %s" % (r["case"], r["predicted"], r["got"], r["rc"],
                                                                      r["stdout"]), flush=True)
        os.makedirs(X10, exist_ok=True)
        json.dump(rows, open(os.path.join(X10, "step0_offline.json"), "w", encoding="utf-8"), indent=1)
        result_line("PASS" if not f else "FAIL", p, f, None if not f else
                    next(r["case"] for r in rows if r["got"] != r["predicted"] or r["rc"]))
        return 0 if not f else 1
    if a.what == "step0-live":
        ev = step0_live(a.cell)
        json.dump(ev, open(os.path.join(X10, "x10c_step0_live.json"), "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)
        for c in ev["calls"]:
            print("CALL %s %s %s | %s" % (c.get("tool"), c.get("decision"), (c.get("cmd") or "")[:160],
                                          c.get("why")), flush=True)
        print("LIVE rc %s calls %d probe_exists %s sentinel_marker %s env_probe_raw_lines %d final %r" % (
            ev["rc"], len(ev["calls"]), ev["probe_exists"], ev["sentinel_marker_exists"], ev["env_probe_raw_lines"],
            (ev["final"] or "")[:300]), flush=True)
        sh = [c for c in ev["calls"] if c.get("kind") == "shell"]
        g = [len(ev["calls"]) >= 3,
             any(c.get("decision") == "ALLOW" and "x10b-live-ok" in (c.get("cmd") or "") for c in sh),
             any(c.get("decision") == "REFUSE" and c.get("kind") != "shell" for c in ev["calls"]),
             not ev["probe_exists"], not ev["sentinel_marker_exists"]]
        # the sentinel's deny may come from layer 2 (guardcore) - cell_guard then logged ALLOW; the codex events
        # and the GPT's own step-3 line are the evidence, printed above / in x10c_step0_live.json
        f = len(g) - sum(g)
        result_line("PASS" if not f else "FAIL", sum(g), f, None if not f else
                    ("calls.jsonl empty - the hook did not run" if not ev["calls"] else "see step0_live.json"))
        return 0 if not f else 1
    rc = run_exec(a.cell, a.prompt, a.model, a.effort)
    print("CODEX_ARM exec rc %s" % rc, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
