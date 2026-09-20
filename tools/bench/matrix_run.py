"""matrix_run.py — unattended GUI-executor matrix: one `claude -p` subprocess per (model, effort).

No agent registry, no user turn: each cell is a fresh print-mode Claude run with the executor task
appended to its system prompt (tools/bench/EXECUTOR_TASK.md). Between cells bench_prep.py resets
LabVIEW. Usage/duration come from the run's JSON result; verified passes come from the trial lines
the cell appends to gui_results.jsonl (matrix_record.py).

  py tools/bench/matrix_run.py --cells haiku-low,sonnet-medium   # explicit cells, in order
  py tools/bench/matrix_run.py --all                              # 20 cells, cheapest first
  py tools/bench/matrix_run.py --all --repeat sonnet-medium=2     # extra repeats after the grid
  py tools/bench/matrix_run.py --cells haiku-low --dry            # print the command only

ALWAYS launch this in the background (it drives the GUI for hours; the PreToolUse guard refuses it
in the foreground). One GUI-driving process at a time: do not run anything else against LabVIEW
while it is running.

Usage-limit protocol (CLAUDE.md §3, user 2026-09-04): a run that ends with a usage/rate-limit
error is INVALID — its partial trial lines are renamed `<method>#interrupted-N` (kept as a
non-result), the driver sleeps until the renewal time + 2 min (parsed from the message; 60 min if
unparsable), then reruns the same cell from the beginning. A run that exceeds CELL_TIMEOUT_S is
killed (process tree), logged INFRA, and rerun once.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
TASK = os.path.join(HERE, "EXECUTOR_TASK.md")
GUI = os.path.join(HERE, "gui_results.jsonl")
LOG = os.path.join(HERE, "matrix_run.log")
RAW = os.path.join(HERE, "matrix_raw")          # one JSON result per attempt
STATUS = os.path.join(PROJECT, "STATUS.md")
MODELS = ["haiku", "sonnet", "opus", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]
CELL_TIMEOUT_S = 40 * 60
MAX_TURNS = 250


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def set_lock(status, purpose=""):
    try:
        s = open(STATUS, encoding="utf-8").read()
        s = re.sub(r"(labview-lock:\n  status: )\w+", rf"\g<1>{status}", s, count=1)
        s = re.sub(r"(  owner:).*", r"\1 " + ("matrix_run.py" if status == "acquired" else ""), s, count=1)
        s = re.sub(r"(  since:).*", r"\1 " + (time.strftime("%Y-%m-%d %H:%M") if status == "acquired" else ""), s, count=1)
        s = re.sub(r"(  purpose:).*", r"\1 " + purpose, s, count=1)
        open(STATUS, "w", encoding="utf-8").write(s)
    except Exception as e:
        log(f"STATUS lock update failed: {e}")


def prep(force_restart=False):
    args = [sys.executable, os.path.join(HERE, "bench_prep.py")] + (["--restart"] if force_restart else [])
    r = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, timeout=400)
    out = (r.stdout.strip().splitlines() or [""])[-1]
    log(f"prep rc={r.returncode} {out[:300]}")
    if r.returncode != 0 and not force_restart:
        return prep(force_restart=True)
    return r.returncode == 0


def claude_cmd(model, effort, method):
    exe = shutil.which("claude") or "claude"
    prompt = (f"You are benchmark cell {method}. Perform the executor task given in your system prompt "
              f"exactly as written, on the LabVIEW instance already running on this machine. Use "
              f"\"{method}\" as the method string in every JSON line you record. Do not ask questions, "
              f"do not negotiate scope, do not touch any VI other than GUIBENCH_v0.vi. When done, reply "
              f"with only the JSON lines.")
    # bypassPermissions: the cell must run lv_gui.ps1 / py tools/* / append to a .jsonl without a
    # human; the project deny list (no Edit/Write on .vi/.ctl/.lvlib/.lvproj) still applies.
    cmd = [exe, "-p", prompt, "--model", model, "--effort", effort, "--output-format", "json",
           "--permission-mode", "bypassPermissions", "--max-turns", str(MAX_TURNS),
           "--append-system-prompt-file", TASK]
    return cmd


def kill_tree(p):
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)


def run_cell(model, effort, attempt):
    method = f"bench-gui-{model}-{effort}"
    cmd = claude_cmd(model, effort, method)
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    env["LV_GUARD_OFF"] = "1"      # the cell's own short GUI calls are not subject to the fg guard
    env["BENCH_CELL"] = method
    # A print-mode cell that backgrounds a command and yields is over (sonnet-low, 2026-09-05:
    # the harness ends background tasks ~5 s after the final result). Documented switch
    # (code.claude.com/docs/en/headless.md, v2.1.4+): every Bash call runs in the foreground.
    env["CLAUDE_CODE_DISABLE_BACKGROUND_TASKS"] = "1"
    shell = cmd[0].lower().endswith((".cmd", ".bat"))
    t0 = time.time()
    # New process group + no console window: the driver died (exit 127 = console control event)
    # the instant the second cell was spawned (2026-09-05 00:49:20); isolate the cell's console
    # control events from the driver.
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    # The cell's JSON goes to a FILE, not a pipe: a driver that dies mid-cell (three times on
    # 2026-09-05) must not take the cell's accounting with it — `--collect` can record it later.
    os.makedirs(RAW, exist_ok=True)
    rawp = os.path.join(RAW, f"{method}-a{attempt}-{time.strftime('%H%M%S')}.json")
    errp = rawp[:-5] + ".stderr.txt"
    with open(rawp, "w", encoding="utf-8") as fo, open(errp, "w", encoding="utf-8") as fe:
        p = subprocess.Popen(subprocess.list2cmdline(cmd) if shell else cmd, cwd=PROJECT, env=env,
                             stdout=fo, stderr=fe, shell=shell, creationflags=flags)
        try:
            p.wait(timeout=CELL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            kill_tree(p)
            p.wait()
            err = open(errp, encoding="utf-8", errors="replace").read()
            return {"status": "TIMEOUT", "seconds": time.time() - t0, "stderr": err[-2000:], "stdout": ""}
    wall = time.time() - t0
    out = open(rawp, encoding="utf-8", errors="replace").read()
    err = open(errp, encoding="utf-8", errors="replace").read()
    try:
        j = json.loads(out)
    except Exception:
        return {"status": "NOJSON", "seconds": wall, "rc": p.returncode, "stderr": err[-2000:], "stdout": out[-2000:]}
    text = (j.get("result") or "") + " " + (err or "")
    # seen 2026-09-05 04:40: "You've hit your session limit · resets 6:20am (Asia/Seoul)"
    limit = re.search(r"(usage|rate|session)[ -]?limit|limit reached|out of (usage|quota)|"
                      r"resets?\s+(at\s+|in\s+)?\d", text, re.I)
    if j.get("is_error") or p.returncode != 0:
        return {"status": "RATE_LIMIT" if limit else "ERROR", "seconds": wall, "rc": p.returncode,
                "json": j, "text": text[-1500:], "raw": rawp, "t0": t0, "t1": time.time()}
    return {"status": "OK", "seconds": wall, "json": j, "raw": rawp, "t0": t0, "t1": time.time()}


def parse_reset(text):
    """Return a datetime for the renewal time, or None. Handles 'resets at 7pm', 'resets 3:30pm',
    'resets in 2 hours 15 minutes', ISO timestamps."""
    now = dt.datetime.now()
    m = re.search(r"resets? (?:at )?(\d{1,2})(?::(\d{2}))?\s*([ap]m)", text, re.I)
    if m:
        h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3).lower()
        h = h % 12 + (12 if ap == "pm" else 0)
        t = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        return t if t > now else t + dt.timedelta(days=1)
    m = re.search(r"resets? in\s+(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?", text, re.I)
    if m and (m.group(1) or m.group(2)):
        return now + dt.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))
    m = re.search(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?)", text)
    if m:
        try:
            return dt.datetime.fromisoformat(m.group(1).replace("T", " "))
        except ValueError:
            pass
    return None


def invalidate_partial(method, tag):
    """Rename the cell's partial trial lines so they stay as a non-result and never count."""
    if not os.path.exists(GUI):
        return 0
    lines = open(GUI, encoding="utf-8").read().splitlines()
    n = 0
    for i, l in enumerate(lines):
        try:
            j = json.loads(l)
        except Exception:
            continue
        if j.get("method") == method:
            j["method"] = f"{method}#{tag}"; j["invalid"] = tag; lines[i] = json.dumps(j, ensure_ascii=False); n += 1
    open(GUI, "w", encoding="utf-8").write("\n".join(lines) + ("\n" if lines else ""))
    return n


def usage_numbers(j):
    u = j.get("usage") or {}
    parts = {k: int(u.get(k, 0) or 0) for k in ("input_tokens", "output_tokens",
                                               "cache_creation_input_tokens", "cache_read_input_tokens")}
    total = sum(parts.values())
    return total, parts, j.get("total_cost_usd"), j.get("duration_ms"), j.get("duration_api_ms"), j.get("num_turns")


ACTIONS_LOG = os.path.join(PROJECT, "tools", "gui_actions.log")


def gated_actions_between(t0, t1):
    """Count lv_gui gated actions logged in [t0, t1] — the machine's own record of what the cell
    actually did, independent of what it reports."""
    n = 0
    try:
        for l in open(ACTIONS_LOG, encoding="utf-8", errors="replace"):
            try:
                ts = time.mktime(time.strptime(l[:19], "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue
            if t0 <= ts <= t1:
                n += 1
    except FileNotFoundError:
        pass
    return n


def salvage_reply_lines(method, text):
    """A cell that only REPLIED with its JSON lines (never appended them) gets them stored as
    unverified claims, so the table can show 'claimed' separately from verified passes."""
    n = 0
    with open(GUI, "a", encoding="utf-8") as fh:
        for m in re.finditer(r"\{[^{}\n]*\"method\"\s*:\s*\"" + re.escape(method) + r"\"[^{}\n]*\}", text):
            try:
                j = json.loads(m.group(0))
            except Exception:
                continue
            j["unverified"] = "reply-only"; j["source"] = "reply"
            fh.write(json.dumps(j, ensure_ascii=False) + "\n"); n += 1
    return n


def lines_for(method):
    if not os.path.exists(GUI):
        return 0
    return sum(1 for l in open(GUI, encoding="utf-8") if l.strip() and json.loads(l).get("method") == method)


def record(method, res):
    j = res["json"]
    total, parts, cost, dur, dur_api, turns = usage_numbers(j)
    appended = lines_for(method)
    salvaged = salvage_reply_lines(method, j.get("result") or "") if appended == 0 else 0
    acted = gated_actions_between(res["t0"], res["t1"])
    note = json.dumps({"cost_usd": cost, "duration_api_ms": dur_api, "num_turns": turns, **parts,
                       "subtype": j.get("subtype"), "raw": os.path.basename(res["raw"]),
                       "gated_actions_logged": acted, "lines_appended": appended, "lines_salvaged": salvaged})
    subprocess.run([sys.executable, os.path.join(HERE, "matrix_record.py"), method, str(total),
                    str(int(dur or res["seconds"] * 1000)), str(turns or 0), note], cwd=PROJECT)


def run_matrix(cells, dry):
    for model, effort in cells:
        method = f"bench-gui-{model}-{effort}"
        if dry:
            print(subprocess.list2cmdline(claude_cmd(model, effort, method))); continue
        attempt, infra_retries = 0, 0
        while True:
            attempt += 1
            if not prep():
                log(f"{method}: LabVIEW prep failed twice — skipping cell"); break
            prior = invalidate_partial(method, f"prior-{time.strftime('%m%d%H%M')}")   # per-attempt counts
            log(f"{method}: attempt {attempt} start" + (f" ({prior} earlier lines set aside)" if prior else ""))
            res = run_cell(model, effort, attempt)
            st = res["status"]
            log(f"{method}: attempt {attempt} -> {st} after {res['seconds']:.0f}s")
            if st == "OK":
                record(method, res); break
            if st == "RATE_LIMIT":
                n = invalidate_partial(method, f"interrupted-{attempt}")
                reset = parse_reset(res["text"])
                wake = (reset + dt.timedelta(minutes=2)) if reset else dt.datetime.now() + dt.timedelta(minutes=60)
                log(f"{method}: usage limit hit ({n} partial lines invalidated); text={res['text'][-300:]!r}; "
                    f"sleeping until {wake:%Y-%m-%d %H:%M} then RERUN from scratch")
                set_lock("released", f"waiting for usage-limit renewal; resume {method} at {wake:%H:%M}")
                time.sleep(max(60, (wake - dt.datetime.now()).total_seconds()))
                set_lock("acquired", "GUI-executor matrix (overnight)")
                continue
            # TIMEOUT / ERROR / NOJSON: one infra retry, then move on
            invalidate_partial(method, f"{st.lower()}-{attempt}")
            log(f"{method}: {st} detail: {str(res.get('text') or res.get('stderr') or res.get('stdout'))[-600:]!r}")
            if infra_retries < 1:
                infra_retries += 1; continue
            break


def main():
    import signal
    for sig in ("SIGINT", "SIGBREAK"):          # survive console control events from the harness/cells
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), signal.SIG_IGN)
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", help="comma list model-effort")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--repeat", default="", help="e.g. sonnet-medium=2,haiku-low=1")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--start-at", default="", help="HH:MM local; sleep until then before the first cell (usage-limit renewal)")
    a = ap.parse_args()
    if a.start_at:
        h, mi = map(int, a.start_at.split(":"))
        t = dt.datetime.now().replace(hour=h, minute=mi, second=0, microsecond=0)
        if t < dt.datetime.now():
            t += dt.timedelta(days=1)
        log(f"start-at {t:%Y-%m-%d %H:%M}: sleeping {(t - dt.datetime.now()).total_seconds():.0f}s")
        time.sleep(max(0, (t - dt.datetime.now()).total_seconds()))
    cells = []
    if a.all:
        cells = [(m, e) for m in MODELS for e in EFFORTS]
    if a.cells:
        cells += [tuple(c.split("-")) for c in a.cells.split(",") if c]
    for item in [x for x in a.repeat.split(",") if x]:
        c, n = item.split("="); cells += [tuple(c.split("-"))] * int(n)
    if not cells:
        ap.error("nothing to run")
    if not a.dry:
        set_lock("acquired", "GUI-executor matrix (overnight)")
        log(f"matrix start: {len(cells)} cells: {' '.join(m+'-'+e for m,e in cells)}")
    try:
        run_matrix(cells, a.dry)
    finally:
        if not a.dry:
            set_lock("released", "")
            log("matrix end")


if __name__ == "__main__":
    main()
