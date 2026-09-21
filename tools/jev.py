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


def summarise_failure(logpath):
    """Compact failure summary of ONE bgrun log's LAST run: script, how it ended, first FAIL line + context (or
    the final traceback / inner-failure line when there is no FAIL line), and the last lines. ≤3200 chars."""
    try:
        with open(logpath, "r", encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
    except OSError:
        return None
    starts = list(_BGRUN_START_RE.finditer(txt))
    if not starts:
        return None
    m = starts[-1]
    cmd, seg = m.group(1), txt[m.end():]
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


def same_failure_class(summary_a, summary_b, purpose="same-failure-class"):
    """Probability that two failure summaries are the same failure class (measured 92.5 % / Brier 0.059 on the
    2026-09-22 40-pair set), or None with an error string."""
    if not summary_a or not summary_b:
        return None, "empty summary"
    resp, err = ask({"log_a": summary_a, "log_b": summary_b}, {"same_failure_class": SAME_FAILURE_Q}, purpose)
    if err:
        return None, err
    p = noul(resp, "same_failure_class")
    return p, (None if p is not None else "no noul in response")
