r"""jev_triage.py - ONE line of first-pass triage for a failing bgrun log (docs/jev-integration-plan.md #2).

    py tools/jev_triage.py tools/bench/<name>.log

prints, and appends to tools/bench/jev_gate.log, exactly one line:

    JEV-TRIAGE | <log> | <class> p=<p> | <the first FAIL/traceback line, <=160 chars>

<class> is one of script-bug / address-invalid / labview-refused / expected-reading, or `unknown` when the
winning probability is below 0.70 (the project's unknown band, tools/jev.py) or there is no key. It is an
ADVISORY SIGNAL, never a gate: nothing refuses anything on the strength of this line, and the log-reader agent
still reads the log. Measured on tools/bench/jev_triage_set.json by tools/bench/jev_triage_trial.py.

Exit code is 0 whenever a line was printed (including `unknown`); 2 only when the log cannot be summarised.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import jev  # noqa: E402

GATELOG = os.path.join(ROOT, "tools", "bench", "jev_gate.log")
THRESHOLD = jev.UNKNOWN_HI          # 0.70
_EVIDENCE_RE = re.compile(r"^\s*(?:\*\*)?(?:FAIL\b|Traceback \(most recent call last\)|BGRUN INNER FAILURE)")


def _question():
    """The measured triage question (tools/bench/jev_triage_q.py, shared with the trial)."""
    from jev_triage_q import TRIAGE_Q
    return TRIAGE_Q


def evidence_line(summary):
    """The first FAIL / traceback / inner-failure line of the summary, else its first non-header line."""
    body = summary.splitlines()
    for ln in body:
        if _EVIDENCE_RE.match(ln):
            return " ".join(ln.split())[:160]
    for ln in body[4:]:
        if ln.strip():
            return " ".join(ln.split())[:160]
    return ""


def triage(logpath):
    """(class, probability_or_None, evidence_line). Never raises."""
    summary = jev.summarise_failure(logpath)
    if not summary:
        return None, None, ""
    ev = evidence_line(summary)
    resp, err = jev.ask({"log": summary}, {"kind": _question()}, purpose="triage")
    if err:
        return "unknown", None, ev
    choice, probs = jev.choice(resp, "kind")
    p = None
    if isinstance(probs, dict) and choice in probs:
        try:
            p = float(probs[choice])
        except (TypeError, ValueError):
            p = None
    if choice is None or p is None or p < THRESHOLD:
        return "unknown", p, ev
    return choice, p, ev


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: py tools/jev_triage.py <bgrun log>\n")
        return 2
    logpath = argv[1] if os.path.isabs(argv[1]) else os.path.join(ROOT, argv[1])
    cls, p, ev = triage(logpath)
    if cls is None:
        sys.stderr.write("JEV-TRIAGE | %s | no bgrun run found in this file\n" % argv[1])
        return 2
    line = "JEV-TRIAGE | %s | %s p=%s | %s" % (
        os.path.basename(logpath), cls, ("%.2f" % p) if p is not None else "-", ev)
    print(line)
    try:
        with open(GATELOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
