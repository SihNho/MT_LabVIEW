# ---
# labview: none
# hardware: none
# ---
"""Live two-agent discussion relay: Claude (claude -p) and GPT (codex exec) take turns on one topic, each resuming its
own session, until both say they are done, the turn cap is hit or a STOP file appears.

User 2026-10-09: "두 에이전트 사이에서 디스커션을 하고 그걸 내가 실시간으로 확인하며 필요시 대화에 참여" /
"실시간으로 대화 진행되는걸 보면서 중간에 필요하면 개입하고 싶다".

Live view: every turn is appended to <dir>/transcript.md AND printed to stdout as one block (the chat watches stdout with
its Monitor tool, so each turn reaches the chat as it is spoken). Stepping in: text appended to <dir>/inbox.md is read
before the next turn and given to BOTH speakers as "사용자:"; the chat writes the user's chat messages there. Stop: create
<dir>/STOP. Each message must end with one line `STATE {"agreed":[..],"open":[..],"experiment":"..","user_needed":"..",
"done":true|false}`.

Usage: py tools/debate_relay.py --dir tools/bench/debate/<slug> --topic <file> [--max-turns 12] [--first claude|gpt]
       [--codex-cwd <dir>] [--dry-run]
Self-test: py tools/debate_relay.py --dry-run --dir %TEMP%/relay_dry --topic <any file> (stub speakers, no model call).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_RE = re.compile(r"^STATE\s+(\{.*\})\s*$", re.M)

RULES = (
    "You are one of two discussants (the other is a different AI model). The user watches every message live and may "
    "step in; lines marked '사용자:' are the user's and override both of you. Rules: write in Korean, plain words, at most "
    "~350 words per message; READ-ONLY - you may read any file of the project but must not change any file, run LabVIEW, "
    "touch hardware or start the cycle runner; cite evidence as file:line; answer the other side's points directly "
    "(agree, rebut with evidence, or revise your position) instead of restating yours; prefer the smallest step that "
    "settles a question. End EVERY message with exactly one line: STATE {\"agreed\":[...],\"open\":[...],"
    "\"experiment\":\"...\",\"user_needed\":\"...\",\"done\":true|false} - done=true only when nothing open remains "
    "that more discussion (not an experiment or the user) could settle.")


def log(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def run(cmd, cwd, stdin_text, env=None, timeout=900):
    """Prompts go on stdin (both CLIs read it), so no quoting or command-line length limit applies."""
    r = subprocess.run(cmd, cwd=cwd, env=env, input=stdin_text, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    return r.returncode, r.stdout, r.stderr


CODEX_JS = os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "@openai", "codex", "bin", "codex.js")


class Claude:
    name = "Claude"

    def __init__(self, a):
        self.sid, self.a = None, a

    def say(self, prompt):
        env = dict(os.environ, BENCH_CELL="1")      # report_gate / guard_session treat it as a cell, not the chat
        cmd = ["claude", "-p", "--model", self.a.claude_model, "--effort", self.a.claude_effort, "--output-format",
               "json", "--allowedTools", "Read", "Glob", "Grep", "--disallowedTools", "Edit", "Write", "Bash",
               "PowerShell", "Agent", "NotebookEdit"]
        if self.sid:
            cmd += ["--resume", self.sid]
        else:
            cmd += ["--append-system-prompt", RULES]
        rc, out, err = run(cmd, ROOT, prompt, env)
        try:
            j = json.loads(out)
            self.sid = j.get("session_id") or self.sid
            return j.get("result") or "", j.get("total_cost_usd")
        except ValueError:
            return "(Claude call failed rc=%d: %s)" % (rc, (err or out)[-400:]), None


class GPT:
    name = "GPT"

    def __init__(self, a):
        self.sid, self.a = None, a

    def say(self, prompt):
        last = os.path.join(self.a.dir, "gpt_last.txt")
        base = ["node", CODEX_JS, "exec"]
        opts = ["--json", "--skip-git-repo-check", "-o", last, "-c", 'model_reasoning_effort="%s"' % self.a.gpt_effort]
        if self.sid:
            cmd, text = base + ["resume", self.sid] + opts + ["-"], prompt
        else:
            cmd, text = base + opts + ["-s", "read-only", "-m", self.a.gpt_model, "-C", self.a.codex_cwd, "-"], \
                RULES + "\n\n" + prompt
        if os.path.exists(last):
            os.remove(last)
        rc, out, err = run(cmd, self.a.codex_cwd, text)
        for line in out.splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            sid = ev.get("thread_id") or ev.get("session_id") or (ev.get("msg") or {}).get("session_id")
            if sid and not self.sid:
                self.sid = sid
        try:
            with open(last, encoding="utf-8") as f:
                return f.read().strip(), None
        except OSError:
            return "(GPT call failed rc=%d: %s)" % (rc, (err or out)[-400:]), None


class Stub:
    def __init__(self, name):
        self.name, self.n = name, 0

    def say(self, prompt):
        self.n += 1
        done = self.n >= 2
        return "%s stub message %d (prompt %d chars)\nSTATE %s" % (
            self.name, self.n, len(prompt), json.dumps({"agreed": [], "open": [] if done else ["x"], "experiment": "",
                                                        "user_needed": "", "done": done})), 0.0


def state_of(msg):
    m = STATE_RE.findall(msg or "")
    try:
        return json.loads(m[-1]) if m else {}
    except ValueError:
        return {}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--max-turns", type=int, default=12)
    ap.add_argument("--first", choices=("claude", "gpt"), default="claude")
    ap.add_argument("--codex-cwd", default=ROOT)
    ap.add_argument("--claude-model", default="claude-opus-5-5")
    ap.add_argument("--claude-effort", default="high")
    ap.add_argument("--gpt-effort", default="high")
    ap.add_argument("--gpt-model", default="gpt-5.6-sol")   # measured 2026-10-09: the CLI on a ChatGPT account refuses gpt-6.1-sol
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.dir, exist_ok=True)
    tr, inbox, stop = (os.path.join(a.dir, n) for n in ("transcript.md", "inbox.md", "STOP"))
    if not os.path.exists(inbox):
        open(inbox, "w", encoding="utf-8").close()
    topic = open(a.topic, encoding="utf-8-sig").read()
    speakers = [Stub("Claude"), Stub("GPT")] if a.dry_run else [Claude(a), GPT(a)]
    if a.first == "gpt":
        speakers.reverse()
    log(tr, "# Discussion %s\n\n## Topic\n\n%s\n" % (time.strftime("%Y-%m-%d %H:%M"), topic))
    print("RELAY START %s dir=%s" % (time.strftime("%H:%M:%S"), a.dir), flush=True)
    seen, last_msg, done_flags, cost = 0, None, {}, 0.0
    for turn in range(1, a.max_turns + 1):
        if os.path.exists(stop):
            print("RELAY STOP (STOP file) after %d turns" % (turn - 1), flush=True)
            break
        user = open(inbox, encoding="utf-8").read()[seen:].strip()
        seen = len(open(inbox, encoding="utf-8").read())
        if user:
            log(tr, "\n### 사용자 (%s)\n\n%s\n" % (time.strftime("%H:%M"), user))
            print("=== 사용자 개입 반영 ===\n%s" % user, flush=True)
        sp = speakers[(turn - 1) % 2]
        parts = []
        if turn <= 2:
            parts.append("## 주제\n" + topic)
        if user:
            parts.append("사용자: " + user)
        if last_msg:
            parts.append("## 상대(%s)의 직전 발언\n%s" % (speakers[turn % 2].name, last_msg))
        parts.append("당신(%s) 차례입니다 (발언 %d/%d)." % (sp.name, turn, a.max_turns))
        t0 = time.time()
        msg, usd = sp.say("\n\n".join(parts))
        cost += usd or 0.0
        st = state_of(msg)
        done_flags[sp.name] = bool(st.get("done"))
        head = "[%d] %s (%s, %ds%s)" % (turn, sp.name, time.strftime("%H:%M"), time.time() - t0,
                                        ", $%.2f" % usd if usd else "")
        log(tr, "\n### %s\n\n%s\n" % (head, msg))
        print("=== %s ===\n%s" % (head, msg), flush=True)
        last_msg = msg
        if len(done_flags) == 2 and all(done_flags.values()):
            print("RELAY CONVERGED after %d turns" % turn, flush=True)
            break
    else:
        print("RELAY TURN CAP %d reached" % a.max_turns, flush=True)
    print("RELAY END %s claude_usd=%.2f transcript=%s" % (time.strftime("%H:%M:%S"), cost, tr), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
