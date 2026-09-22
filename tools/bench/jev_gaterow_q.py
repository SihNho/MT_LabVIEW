r"""jev_gaterow_q.py - the ONE gate-row question and row extractor for docs/jev-integration-plan.md 2차 #2.

Kept in one file so the measurement (tools/bench/jev_wave2a_trials.py) and the tool (tools/jev_gaterow.py) ask the
SAME question over the SAME state: a tool that asks a different question from the one that was measured is not the
measured tool (the rule tools/bench/jev_triage_q.py already carries).

WHAT ALREADY EXISTS (checked before writing, per the material-session rule):
  - tools/jev.py                  -> key handling, retries, ledger, `ask_n` consensus, `summarise_failure`.
                                     REUSED; nothing here makes an HTTP call or reads a key.
  - tools/bench/jev_triage_q.py   -> the WHOLE-RUN triage question (4 classes, "who has to fix it"). DIFFERENT
                                     question: that one classifies a run by its FIRST failure; this one classifies
                                     EVERY failing row of a run, on the axis "is the artefact wrong, or is the
                                     gate wrong, or is the READER wrong". Neither subsumes the other, and the
                                     class lists do not overlap.
  - tools/logclass.py, tools/hooks/guard_peer.FAILURE_RE -> what counts as a failing row. The FAIL pattern here
                                     is guard_peer's `^\s*\*{0,2}FAIL\b` (the bold form included, for the same
                                     reason recorded there), not a third copy invented for this file.

NO NORMALISATION OF THE ROW, deliberately. jev.normalise replaces `#\d+` and any 3+ digit run with '#', which is
right for "are these two failures the same" but destroys exactly the evidence this question turns on: K2's
`Wire 1905` vs the measured `Wire 1906`, D7's `(60, 48) -> (60, 47)`. The row is truncated, never rewritten.
"""
import os
import re

CLASSES = ["defect", "prediction-error", "reading-artefact"]

GATEROW_Q = {
    "type": "choice",
    "instructions": (
        "A LabVIEW VI-scripting project runs each build and diagnostic under a prediction contract: every check "
        "prints one row, `PASS` or `FAIL`, whose text states what was expected and then what was measured. ONE "
        "failing row is given as `row`, with the lines around it as `context` and the run's own header as `run`. "
        "Decide WHY this row failed, so a judgement session knows whether anything is actually wrong. Read the "
        "row's own evidence - the values after the expectation - and judge that, not the tone of the wording."),
    "criteria": {
        "defect": (
            "The artefact or the edit really is wrong, and the row reports it correctly. The VI ends broken "
            "(ExecState 0 after a mutation), an operation did nothing it claimed to do (no object minted, no "
            "count moved), a wire landed on the wrong terminal or stayed broken, an old source was left on a "
            "net, a real resource leak, or our own code raised where it must not. Someone must fix something."),
        "prediction-error": (
            "The machine reading is fine and the GATE's expectation was wrong. The measured value is the correct "
            "one and the predicted number, name, position or ordering was mis-derived; or the row is a "
            "bookkeeping consequence of a stage that was deliberately skipped, deferred or not reached, so "
            "nothing was measured at all. Fixing the expectation (or the plan) clears the row; the VI is fine."),
        "reading-artefact": (
            "Neither the artefact nor the expectation is wrong - the READER could not see the thing. A census or "
            "property read returned nothing, None, zero or an error (1055, 'not found', no Nodes[] index, an "
            "empty terminal table, a class that this COM path cannot enumerate), and the row reports that "
            "no-answer as if it were a measurement. The evidence says the tool is blind here, not that the VI is "
            "wrong."),
    },
}

FAIL_RE = re.compile(r"^\s*\*{0,2}FAIL\b")          # tools/hooks/guard_peer.py FAILURE_RE's row half
_START_RE = re.compile(r"^BGRUN START \S+ \S+ limit [\d.]+ min: (.+)$", re.M)
_END_RE = re.compile(r"^BGRUN (?:END rc=(\d+)|TIMEOUT killed)", re.M)
_SCRIPT_RE = re.compile(r"([\w.-]+\.py)\b")
_LABEL_RE = re.compile(r"^\s*\*{0,2}FAIL\*{0,2}\s+\[?([\w().-]+)")

CTX_BEFORE, CTX_AFTER = 4, 4        # "8 lines of context" (docs/jev-integration-plan.md 2차 #2)


def run_segment(logpath, run_index=-1):
    """(command, segment text, how it ended) for one BGRUN run of a log, or (None, None, None)."""
    try:
        with open(logpath, "r", encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
    except OSError:
        return None, None, None
    starts = list(_START_RE.finditer(txt))
    if not starts:
        return None, None, None
    try:
        m = starts[run_index]
    except IndexError:
        return None, None, None
    end = starts[run_index + 1].start() if -1 < run_index < len(starts) - 1 else len(txt)
    seg = txt[m.end():end]
    f = _END_RE.search(seg)
    ended = "TIMEOUT" if (f and f.group(1) is None) else ("rc=" + f.group(1) if f else "?")
    return m.group(1), seg, ended


def fail_rows(logpath, run_index=-1, max_rows=None):
    """Every FAIL row of one run, as [{'line': n, 'label': 'D7', 'row': ..., 'state': {...}}, ...]."""
    cmd, seg, ended = run_segment(logpath, run_index)
    if seg is None:
        return []
    sm = _SCRIPT_RE.search(cmd or "")
    header = "log: %s\nscript: %s\ncommand: %s\nended: %s" % (
        os.path.basename(logpath), sm.group(1) if sm else "?", " ".join((cmd or "").split())[:240], ended)
    lines = seg.splitlines()
    out = []
    for i, ln in enumerate(lines):
        if not FAIL_RE.match(ln):
            continue
        row = " ".join(ln.split())[:600]
        lm = _LABEL_RE.match(ln)
        ctx = [" ".join(x.split())[:200] for x in lines[max(0, i - CTX_BEFORE):i + CTX_AFTER + 1] if x.strip()]
        out.append({"line": i, "label": (lm.group(1) if lm else "?")[:24], "row": row,
                    "state": {"run": header, "row": row, "context": "\n".join(ctx)[:2200]}})
        if max_rows and len(out) >= max_rows:
            break
    return out
