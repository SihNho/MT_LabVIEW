r"""jev.py - the ONE place this project talks to TypeSafe's Jev (docs/jev-integration-plan.md, user 2026-09-22).

Jev is a typed-decision model: it answers choice / score / yes-no (noul) questions with calibrated probabilities,
never text. Every insertion point in this project imports from here so that the key handling, retries and the
usage ledger are identical everywhere.

KEY: read from the USER environment variable TYPESAFE_API_KEY (os.environ first, then HKCU\Environment for a
process started before the variable was set). The value is NEVER printed, logged, written or passed as an
argument. If it is missing, every call returns (None, "no key") and the caller falls back to its old path.

LEDGER: tools/bench/jev_usage.jsonl - one line per call: purpose, latency, tokens, http status. No payloads.

    from tools import jev        # or: import jev (tools/ on sys.path)
    p, err = jev.same_failure_class(summary_a, summary_b)     # noul probability or None
    ans, err = jev.ask({"log": text}, {"kind": {"type": "choice", "instructions": "...", "criteria": {...}}})
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
LEDGER = os.path.join(BENCH, "jev_usage.jsonl")
UNKNOWN_LO, UNKNOWN_HI = 0.30, 0.70     # probabilities inside this band mean "unknown" -> the old path decides


def get_key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if k:
        return k
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            v, _ = winreg.QueryValueEx(h, "TYPESAFE_API_KEY")
            if v:
                return v
    except Exception:
        pass
    return None


def _ledger(purpose, latency, resp, status):
    try:
        usage = None
        if isinstance(resp, dict):
            for k in ("usage", "token_usage", "tokens"):
                if k in resp:
                    usage = resp[k]
                    break
        os.makedirs(BENCH, exist_ok=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "purpose": purpose,
                                "latency_s": round(latency, 3), "usage": usage, "status": status}) + "\n")
    except OSError:
        pass


def ask(state, questions, purpose="unspecified", timeout=60, retries=3):
    """POST one request. Returns (response_dict, None) or (None, error_string). Never raises."""
    key = get_key()
    if not key:
        _ledger(purpose, 0.0, None, "no key")
        return None, "no key"
    body = json.dumps({"model": MODEL, "state": state, "questions": questions}).encode("utf-8")
    delay, last = 3.0, None
    for attempt in range(retries + 1):
        req = urllib.request.Request(API_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + key)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read().decode("utf-8", "replace"))
            _ledger(purpose, time.time() - t0, resp, "ok")
            return resp, None
        except urllib.error.HTTPError as e:
            last = "HTTP %s %s" % (e.code, e.read().decode("utf-8", "replace")[:200])
            if e.code in (429, 529) and attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            _ledger(purpose, time.time() - t0, None, last[:40])
            return None, last
        except Exception as e:  # noqa: BLE001 - network/timeout/parse: report, never raise
            last = "%s: %s" % (type(e).__name__, str(e)[:200])
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            _ledger(purpose, time.time() - t0, None, last[:40])
            return None, last
    return None, last


SAMPLES_DEFAULT = 5     # docs/jev-integration-plan.md 2차 #6, user-approved 2026-09-22 17:3x


def samples(default=SAMPLES_DEFAULT):
    """How many times one question is asked before its answer is used. `JEV_SAMPLES` overrides (1..25)."""
    raw = os.environ.get("JEV_SAMPLES", "")
    if not raw:
        return default
    try:
        return max(1, min(25, int(raw)))
    except ValueError:
        return default


def ask_n(state, questions, n=None, purpose="unspecified", timeout=60, retries=3):
    """CONSENSUS: ask ONE question `n` times (sequentially, each with ask()'s own retries) and average.

    Returns (mean, spread, error):
      * noul question   -> mean is the MEAN yes-probability (float); spread is max-min of the n readings.
      * choice question -> mean is a dict {option: mean probability}; spread is max-min of the readings for
                           the option that WINS on the mean, so the spread describes the answer actually used.
      * spread is a dict {'spread': float, 'n': asked, 'n_ok': answered, 'values': [...]} - the caller logs
        the float and ignores the rest; `spread['n_ok'] < n` means some calls failed and were dropped.
      * on no usable answer at all: (None, None, error string).

    WHY. The same (log, review) pair read p = 0.80, 0.78, 0.80, 0.79 within twenty minutes on 2026-09-22, so a
    0.80 threshold flapped allow/block on consecutive commands (the decision cache in tools/bench/jev_gate.py was
    the first, narrower patch for that). One call is a sample, not a reading; the mean of five is what the
    thresholds in this project are compared against from 2026-09-22.

    NOT PARALLEL, deliberately: a PreToolUse hook must stay inside its own bounded time, and this project has one
    measured cost figure per call, not per connection. Five sequential calls at the measured 0.56 s are ~3 s.
    """
    n = samples() if n is None else max(1, int(n))
    try:
        name = next(iter(questions))
    except StopIteration:
        return None, None, "no question"
    q = questions[name]
    kind = (q.get("type") if isinstance(q, dict) else None) or "noul"
    vals, probs_acc, last_err, n_ok = [], {}, None, 0
    for _ in range(n):
        resp, err = ask(state, questions, purpose, timeout=timeout, retries=retries)
        if err:
            last_err = err
            continue
        if kind == "choice":
            ch, pr = choice(resp, name)
            if ch is None or not isinstance(pr, dict):
                last_err = "no choice in response"
                continue
            for k, v in pr.items():
                try:
                    probs_acc.setdefault(k, []).append(float(v))
                except (TypeError, ValueError):
                    pass
            n_ok += 1
        else:
            p = noul(resp, name)
            if p is None:
                last_err = "no noul in response"
                continue
            vals.append(p)
            n_ok += 1
    if not n_ok:
        return None, None, (last_err or "no answer")
    if kind == "choice":
        mean = {k: sum(v) / len(v) for k, v in probs_acc.items() if v}
        if not mean:
            return None, None, (last_err or "no probabilities in any response")
        winner = max(mean, key=mean.get)
        vals = probs_acc.get(winner, [])
    spread = (max(vals) - min(vals)) if vals else 0.0
    if kind != "choice":
        mean = sum(vals) / len(vals)
    return mean, {"spread": spread, "n": n, "n_ok": n_ok, "values": [round(v, 4) for v in vals]}, None


def noul(resp, name=None):
    """The yes-probability of a noul answer (by question name when given), or None."""
    if not isinstance(resp, dict):
        return None
    answers = resp.get("answers") if isinstance(resp.get("answers"), dict) else None
    if answers and name in answers and isinstance(answers[name], dict):
        v = answers[name].get("noul")
        return float(v) if isinstance(v, (int, float)) else None
    stack = [resp]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if cur.get("type") == "noul" and isinstance(cur.get("noul"), (int, float)):
                return float(cur["noul"])
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return None


def choice(resp, name):
    """(chosen option, probabilities dict) of a choice answer, or (None, None)."""
    try:
        a = resp["answers"][name]
        return a.get("choice"), a.get("probabilities")
    except Exception:
        return None, None


def verdict(p):
    """'yes' / 'no' / 'unknown' from a probability, using the project's unknown band."""
    if p is None:
        return "unknown"
    if p >= UNKNOWN_HI:
        return "yes"
    if p <= UNKNOWN_LO:
        return "no"
    return "unknown"


# ---------------------------------------------------------------------------------------------------------------
# Failure-log summaries (ported from tools/bench/jev_trial.py, the measured 40-pair trial of 2026-09-22)

_BGRUN_START_RE = re.compile(r"^BGRUN START \S+ \S+ limit [\d.]+ min: (.+)$", re.M)
_BGRUN_FAIL_RE = re.compile(r"^BGRUN (?:END rc=(\d+)|TIMEOUT killed)", re.M)
_SCRIPT_RE = re.compile(r"([\w.-]+\.py)\b")
_FAIL_LINE_RE = re.compile(r"^\s*(?:\*\*)?FAIL(?:\*\*)?\s", re.M)
_INNER_FIRST_RE = re.compile(r"^BGRUN INNER FAILURE:.*$", re.M)


def normalise(s):
    s = re.sub(r"\b[0-9a-f]{32}\b", "<md5>", s)
    s = re.sub(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", "<ts>", s)
    s = re.sub(r"#\d+", "#", s)
    s = re.sub(r"\b\d{3,}\b", "#", s)
    return s.replace(ROOT, "<root>")


def summarise_failure(logpath, run_index=-1):
    """Compact failure summary of ONE bgrun log's LAST run: script, how it ended, first FAIL line + context (or
    the final traceback / inner-failure line when there is no FAIL line), and the last lines. ≤3200 chars.

    `run_index` selects which `BGRUN START` block to summarise (-1 = the last, the only behaviour before
    2026-09-22). A log is appended to, so a run that was reviewed hours ago is no longer the last one:
    tools/bench/diag_c83_connect2x2_kit.log's reviewed failure is run 0 and its last two runs ended rc=0.
    Only a measurement over a FIXED past run can be scored against what a reviewer actually saw."""
    try:
        with open(logpath, "r", encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
    except OSError:
        return None
    starts = list(_BGRUN_START_RE.finditer(txt))
    if not starts:
        return None
    try:
        m = starts[run_index]
    except IndexError:
        return None
    end = starts[run_index + 1].start() if -1 < run_index < len(starts) - 1 else len(txt)
    cmd, seg = m.group(1), txt[m.end():end]
    f = _BGRUN_FAIL_RE.search(seg)
    ended = "TIMEOUT" if (f and f.group(1) is None) else ("rc=" + f.group(1) if f else "?")
    sm = _SCRIPT_RE.search(cmd)
    script = sm.group(1) if sm else "?"
    lines = seg.splitlines()
    fl = _FAIL_LINE_RE.search(seg)
    if fl:
        idx = seg[:fl.start()].count("\n")
        body, where = lines[max(0, idx - 4):min(len(lines), idx + 11)], "first FAIL line + context"
    else:
        tb = seg.rfind("Traceback (most recent call last)")
        if tb >= 0:
            idx = seg[:tb].count("\n")
            body, where = lines[idx:idx + 15], "final traceback"
        else:
            im = _INNER_FIRST_RE.search(seg)
            if im:
                body, where = [im.group(0)], "bgrun inner-failure line"
            else:
                body, where = [ln for ln in lines if ln.strip()][-15:], "last non-empty lines"
    body = [ln[:300] for ln in body]
    tail = [ln[:300] for ln in lines if ln.strip()][-6:]
    s = "log: %s\nscript: %s\nended: %s\nextract: %s\n%s\n--- how the run ended (last lines) ---\n%s" % (
        os.path.basename(logpath), script, ended, where, "\n".join(body), "\n".join(tail))
    return normalise(s)[:3200]


SAME_FAILURE_Q = {
    "type": "noul",
    "instructions": (
        "Two failing build logs from one LabVIEW VI-scripting project are given as log_a and log_b. Each is a "
        "compact extract: the script that ran, how the run ended, and the first failing gate line with context "
        "(uids and long numbers are replaced by '#'). Decide whether they fail for the SAME underlying reason - "
        "i.e. whether one fix would clear both. Judge the defect, not the file names: two different scripts can "
        "hit one defect, and one script can fail two unrelated ways on different runs."),
    "criteria": {
        "true": ("The two runs are blocked by the same underlying defect, so a single fix would clear both. "
                 "Examples: the same script re-run with no change; a diagnostic written to reproduce a build's "
                 "failure, hitting the identical gate; two runs stopped by one broken operation."),
        "false": ("The two runs are blocked by different underlying defects, so fixing one would leave the other "
                  "failing. This includes consecutive versions of one script that got past the earlier defect and "
                  "died on a new one, and two unrelated defects that merely share the tool that reported them."),
    },
}


def same_failure_class(summary_a, summary_b, purpose="same-failure-class", n=None):
    """Probability that two failure summaries are the same failure class (measured 92.5 % / Brier 0.059 on the
    2026-09-22 40-pair set), or None with an error string.

    CONSENSUS OF `samples()` CALLS since 2026-09-22 (2차 #6): the firefighter rule turns a cycle on p <= 0.30,
    and a single sample of a probability near a threshold is the coin-flip this project already measured. The
    signature is unchanged so tools/cycle_runner.py needs no edit."""
    if not summary_a or not summary_b:
        return None, "empty summary"
    p, _spread, err = ask_n({"log_a": summary_a, "log_b": summary_b},
                            {"same_failure_class": SAME_FAILURE_Q}, n=n, purpose=purpose)
    return (p, None) if p is not None else (None, err or "no noul in response")
