r"""jev_gate.py - the ONE definition of the two Jev-backed gate questions (docs/jev-integration-plan.md rows #1
and #6, user 2026-09-22 "Jev를 적용해 사이클 시간을 줄여라").

NO LabVIEW. This module reads .log and .md files off disk and, through tools/jev.py ONLY, makes HTTPS calls to
api.typesafe.ai. No COM, no VISA, no motor, no camera, no GUI, no .vi.

WHAT ALREADY EXISTS (checked before writing, per the material-session rule):
  - tools/jev.py                -> key handling, retries, the usage ledger, `summarise_failure`, `verdict`,
                                   `same_failure_class` (insertion #3, already wired into cycle_runner).
                                   REUSED. Nothing here re-implements an HTTP call or a key read.
  - tools/bench/jev_trial.py    -> the measured 40-pair trial of insertion #3. Its summariser was promoted into
                                   jev.py; this module reuses jev.summarise_failure rather than copying it.
  - tools/hooks/guard_peer.py   -> review_quality(), ADVERSARY_AGENTS, CLAUDE_ADVERSARY_ROLE. REUSED by import,
                                   not restated, so "what counts as a review" has one definition.
  - tools/logclass.py           -> build-vs-machinery log. Used by the trial's set builder.
  - no existing review-summariser, duplicate-detector or gate-advisory logger was found under tools/.

WHY A tools/bench/ MODULE AND NOT tools/jev.py. The brief's editable surface is guard_peer.py, prior_art_review.py
and new tools/bench/jev_*.py files; jev.py is the shared transport and is left byte-unchanged. Both call sites and
both trials import THIS file, so the questions, the thresholds and the log format exist once.

THRESHOLDS (docs/jev-integration-plan.md "공통 원칙": 0.3-0.7 is "unknown" -> the old path decides).
  discharge  p >= DISCHARGE_P (0.80)  -> the gate allows and CITES the review it relied on
             ADVISORY_LO < p < 0.80   -> the gate blocks exactly as before, plus one JEV-ADVISORY line
             p <= 0.30 / no key / err -> the gate blocks exactly as before, silently
  prior-art  p >= DUP_P (0.85)        -> ADVISORY ONLY. One JEV-PRIORART-DUP line; nothing is blocked.
"""
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))          # ...\tools\bench
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
PEER = os.path.join(ROOT, "archive", "peer")
GATE_LOG = os.path.join(HERE, "jev_gate.log")

if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
import jev  # noqa: E402

DISCHARGE_P = 0.80   # user 2026-09-22: start at 0.80 (sweep: 0.70 and 0.85 both precision 1.0 on the 40-pair set), re-tune after 3 cycles
DUP_P = 0.85
ADVISORY_LO = 0.30
N_RECENT_REVIEWS = 5
CALL_TIMEOUT = 25          # a PreToolUse hook must never hang the session on a network stall
CALL_RETRIES = 1

DISPOSITION_H = "## What was done with it"


# --------------------------------------------------------------------------------------------- review summaries
_Q_RE = re.compile(r"^## Question\s*$(.*?)(?=^## Answer\s*$|\Z)", re.M | re.S)
_VERDICT_RE = re.compile(r"^(?:VERDICT|PRIOR-ART|## VERDICT)[^\n]{0,200}$", re.M)
_HEAD_RE = re.compile(r"^\-\s*\*\*(agent|role|kind|outcome|date):\*\*\s*(.+)$", re.M)


def summarise_review(path, qchars=2500):
    """What the gate hands Jev about ONE archived peer exchange: its identity line, the first `qchars` of the
    question it was asked, and its verdict/summary lines. Returns None when the file cannot be read.

    The QUESTION is the part that decides coverage: a review is 'about' whatever failure or step its task named.
    The answer's verdict lines are appended because a review that refuted its own framing covers the failure
    differently from one that confirmed it."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read().lstrip("﻿")
    except OSError:
        return None
    head = "; ".join("%s=%s" % (k, " ".join(v.split())[:60]) for k, v in _HEAD_RE.findall(body))
    m = _Q_RE.search(body)
    q = (m.group(1) if m else body)[:qchars]
    verdicts = _VERDICT_RE.findall(body.split("\n## Answer", 1)[-1])[:6]
    s = "review: %s\n%s\n--- the question this review was asked (first %d chars) ---\n%s\n--- verdict lines ---\n%s" % (
        os.path.basename(path), head, qchars, q, "\n".join(v.strip()[:200] for v in verdicts) or "(none)")
    return jev.normalise(s)[:4000]


def review_meta(path):
    """(agent, role, outcome) lowercased, '' where absent."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read()
    except OSError:
        return "", "", ""
    d = {k.lower(): v.strip().lower() for k, v in _HEAD_RE.findall(body)}
    return d.get("agent", ""), d.get("role", ""), d.get("outcome", "").split()[0] if d.get("outcome") else ""


def recent_adversary_reviews(n=N_RECENT_REVIEWS, before=None):
    """The `n` newest archived exchanges that guard_peer would ACCEPT as a failed-prediction review, newest first.

    'Accept' is guard_peer.review_quality's own answer, imported rather than restated - so if the project ever
    changes who may discharge a failed prediction, this follows automatically. `before` (a unix time) keeps a
    trial honest: only reviews that already existed when the log failed may be offered as covering it."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
    try:
        import guard_peer
    except Exception:
        return []
    out = []
    for p in glob.glob(os.path.join(PEER, "*.md")):
        b = os.path.basename(p)
        if re.search(r"priorart|retrospective|outcome-review", b, re.I):
            continue
        try:
            st = os.stat(p)
            born = min(st.st_ctime, st.st_mtime) if os.name == "nt" else st.st_mtime
            if before is not None and born > before:
                continue
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                body = fh.read()
        except OSError:
            continue
        ok, _ = guard_peer.review_quality(body)
        if ok and "## Question" in body:
            out.append((born, p))
    out.sort(reverse=True)
    return [p for _, p in out[:n]]


# --------------------------------------------------------------------------------------------- the questions
COVERS_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW VI-scripting project blocks its next build whenever a run's stated prediction fails, until a "
        "peer review of THAT failure has been archived. `failure` is a compact extract of the failing run (the "
        "script, how it ended, the first failing gate line with context; uids and long numbers replaced by '#'). "
        "`review` is an archived adversarial peer review: the question it was asked, and its verdict lines. "
        "Decide whether that archived review ALREADY covers this failure - the same underlying defect, so its "
        "analysis and its recommendation apply and a fresh review would only re-ask what has been answered. "
        "Judge the defect, not the file names or the dates."),
    "criteria": {
        "true": ("The review was asked about this very failure, or about a defect that is the same one under "
                 "another run or another file name - e.g. the review attacks the prediction that this run's first "
                 "failing gate reports, or a later run of the same script failing at the same place for the same "
                 "reason. Acting on the archived review would address this failure."),
        "false": ("The review is about a different defect, even if it shares the script, the stage, the tool that "
                  "reported it, or the day. This includes the NEXT failure of a script that was repaired after "
                  "the review, a different gate of the same checker, and a different row or stage of the same "
                  "build. Someone reading only that review would not know what went wrong here."),
    },
}

STEP_ANSWERED_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW VI-scripting project runs a 'prior-art' review before each build step, asking whether that step "
        "has already been analysed here. `step` is one planned step, stated in a sentence or two. `review` is an "
        "archived prior-art review: the plan text it was given, and its verdict lines. Decide whether that "
        "archived review ALREADY answers this exact step's question, so dispatching a new prior-art review would "
        "only re-ask it. Judge the work under review, not the wording or the date."),
    "criteria": {
        "true": ("The archived review was asked about this same step - the same stage of the same build, the same "
                 "recipe (including a later edit round of it when the step IS that edit round), the same "
                 "decomposition. Its findings apply to this step as stated."),
        "false": ("The review is about a different step: a neighbouring stage, a different recipe for the same "
                  "stage, an earlier version of a recipe when the step is a later authorised edit round (or the "
                  "reverse), or the whole plan rather than this step. Someone holding only that review would still "
                  "have to ask about this step."),
    },
}


def covers_failure(failure_summary, review_summary, purpose="guard-peer-discharge", n=None):
    """Probability that `review_summary` already covers `failure_summary`. (p, None) or (None, error).

    CONSENSUS since 2026-09-22 (2차 #6): the MEAN of `jev.samples()` asks, because DISCHARGE_P is 0.80 and this
    very pair was measured reading 0.80 / 0.78 / 0.80 / 0.79 within twenty minutes - the flapping the decision
    cache below was the first patch for. The cache stays: it makes a GRANTED discharge final, which consensus
    does not do on its own."""
    if not failure_summary or not review_summary:
        return None, "empty summary"
    p, _spread, err = jev.ask_n({"failure": failure_summary, "review": review_summary},
                                {"review_covers_failure": COVERS_Q}, n=n, purpose=purpose,
                                timeout=CALL_TIMEOUT, retries=CALL_RETRIES)
    return (p, None) if p is not None else (None, err or "no noul in response")


def answers_step(step_sentence, review_summary, purpose="priorart-duplicate"):
    """Probability that `review_summary` already answers `step_sentence`. (p, None) or (None, error)."""
    if not step_sentence or not review_summary:
        return None, "empty summary"
    resp, err = jev.ask({"step": step_sentence, "review": review_summary},
                        {"review_answers_step": STEP_ANSWERED_Q}, purpose,
                        timeout=CALL_TIMEOUT, retries=CALL_RETRIES)
    if err:
        return None, err
    p = jev.noul(resp, "review_answers_step")
    return p, (None if p is not None else "no noul in response")


# --------------------------------------------------------------------------------------------- the audit trail
def gate_log(line):
    """One line to tools/bench/jev_gate.log. Never raises: a gate must not die on a full disk."""
    try:
        with open(GATE_LOG, "a", encoding="utf-8") as fh:
            fh.write(line.rstrip("\n") + "\n")
    except OSError:
        pass


def cite_in_review(review_path, log_name, p, ts=None):
    """Write the discharge citation into the review file under `## What was done with it`, so the audit and
    doc_lint see WHY a build ran with no new review. Returns True when it landed.

    DELIBERATELY NOT A RELEASE LINE: nothing here starts with `FIXED:`, `REFUTED:` or `PRIOR-ART:` (the three
    line-anchored patterns guard_cycle.py matches), so citing a discharge cannot release a prior-art verdict.
    It also does not move the file's CREATION time, which is what guard_peer's own binding test reads - so this
    cannot retro-bind an old review to a new failure by a side effect."""
    ts = ts or time.strftime("%Y-%m-%d %H:%M:%S")
    line = "JEV-DISCHARGE: %s (%s, p=%.3f)" % (log_name, ts, p)
    try:
        with open(review_path, "r", encoding="utf-8", errors="replace") as fh:
            body = fh.read()
        with open(review_path, "a", encoding="utf-8") as fh:
            if DISPOSITION_H not in body:
                fh.write("\n\n" + DISPOSITION_H + "\n")
            fh.write("\n" + line + "\n  This failing run was released without a NEW peer review: Jev judged, at "
                     "the probability shown, that the failure above is the one this review already attacks "
                     "(tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the "
                     "evidence; this line only records which failure was charged to it.\n")
        return True
    except OSError:
        return False


def jev_discharge(log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True):
    """THE GATE CALL (guard_peer.py). Returns (allow, reason_line).

    allow=True  -> the newest accepted reviews contain one that covers this failure at p >= DISCHARGE_P. The
                   citation is logged AND written into that review file.
    allow=False -> block exactly as before. reason_line is a JEV-ADVISORY string when some review scored inside
                   the unknown band, else None (no key, an API error, or every review clearly unrelated).

    NEVER RAISES and never blocks longer than the bounded calls: any exception means the old behaviour."""
    try:
        # DECISION CACHE (2026-09-22 11:4x): the same (log, review) pair read p=0.80, 0.78, 0.80, 0.79 within
        # twenty minutes, so the gate flapped allow/block on consecutive commands. A discharge, once granted and
        # CITED in the review file, is final for that log - the citation is already on record.
        cache_path = os.path.join(os.path.dirname(GATE_LOG), "jev_discharge_cache.json")   # beside the gate log, so a redirected GATE_LOG isolates the cache too
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
        hit = cache.get(os.path.basename(log_path))
        if isinstance(hit, dict) and hit.get("review"):
            return True, "JEV-DISCHARGE | cached | %s covered by %s p=%.3f (granted %s)" % (
                os.path.basename(log_path), hit["review"], float(hit.get("p", 0)), hit.get("ts", "?"))
        if not jev.get_key():
            return False, None
        fs = jev.summarise_failure(log_path) or jev.normalise(failure_text or "")[:3200]
        if not fs:
            return False, None
        best = (None, None)
        for rp in recent_adversary_reviews(n, before=before):
            p, err = covers_failure(fs, summarise_review(rp))
            if p is None:
                continue
            if best[0] is None or p > best[0]:
                best = (p, rp)
            if p >= DISCHARGE_P:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                line = "JEV-DISCHARGE | %s | %s covered by %s p=%.3f" % (
                    ts, os.path.basename(log_path), os.path.basename(rp), p)
                if write:
                    gate_log(line)
                    cite_in_review(rp, os.path.basename(log_path), p, ts)
                    try:
                        cache[os.path.basename(log_path)] = {"review": os.path.basename(rp), "p": p, "ts": ts}
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(cache, f, indent=1)
                    except Exception:
                        pass
                return True, line
        if best[0] is not None and best[0] > ADVISORY_LO:
            line = "JEV-ADVISORY | %s | %s closest review %s p=%.3f (< %.2f: blocking as before)" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(log_path),
                os.path.basename(best[1]), best[0], DISCHARGE_P)
            if write:
                gate_log(line)
            return False, line
        return False, None
    except Exception:                       # noqa: BLE001 - a gate must degrade to its old behaviour, never wedge
        return False, None


# --------------------------------------------------------------------------------------------- THE REVIEW LADDER
# docs/jev-integration-plan.md 2차 #1, USER-APPROVED 2026-09-22 17:3x ("이거 다 적용해보자"). This is the one
# insertion in the Jev plan that is a RULE CHANGE and not a mechanisation: CLAUDE.md section 5 says a failed
# prediction owes an adversarial review, full stop. The ladder says that three kinds of "failed prediction" reach
# this gate and only one of them is the kind the rule was written for:
#
#   our-script-bug        our own Python died, or every failing row is the GATE's own arithmetic being wrong.
#                         Nothing about the LabVIEW machine is in dispute, so there is no framing for an
#                         adversary to attack. Measured on today's own reviews before wiring.
#   already-reviewed-class  a review of this very defect is already archived - the case CLAUDE.md section 5
#                         already covers in prose ("check archive/peer/ for the same question before re-asking").
#                         This branch does NOT trust the ladder: it runs the ORDINARY discharge, which can only
#                         ever cite an exchange that passed review_quality(). A review that TIMED OUT is not
#                         citable, so a class that "was reviewed" but never answered still blocks.
#   new-problem           the rule applies unchanged: fall through to the old path, which blocks.
#
# ACTS ONLY AT p >= LADDER_P on the CONSENSUS mean of jev.samples() asks. No key, an error, an unknown band or
# ANY exception => the old path, byte for byte.
LADDER_P = 0.80
LADDER_CLASSES = ["our-script-bug", "already-reviewed-class", "new-problem"]
LADDER_ALLOWED = os.path.join(HERE, "jev_ladder_allowed.jsonl")
LADDER_Q = {
    "type": "choice",
    "instructions": (
        "A LabVIEW VI-scripting project blocks its next build whenever a run's stated prediction fails, until an "
        "expensive adversarial peer review of THAT failure has been archived. `failure` is a compact extract of "
        "the failing run: the script, how it ended, the first failing gate row with context. `gate_rows`, when "
        "present, is a per-row verdict on EVERY failing row of the same run - `defect` (the artefact really is "
        "wrong), `prediction-error` (the gate's expectation was wrong and the machine reading is fine) or "
        "`reading-artefact` (a census or property read could not see the thing). `recent_reviews`, when present, "
        "lists the questions the newest archived reviews were asked. Decide which ONE of three kinds this "
        "failure is, so the project knows whether the review is worth buying."),
    "criteria": {
        "our-script-bug": (
            "Nothing about the machine is in dispute. Our own Python raised (traceback, import, name, format or "
            "path error), or a static checker of our own recipes refused them, or the run never reached LabVIEW "
            "- OR every failing row is a `prediction-error`, i.e. the measured values are right and only the "
            "expectation was mis-derived. Fixing our own file clears it; an adversary has no framing to attack."),
        "already-reviewed-class": (
            "The same underlying defect is one the listed recent reviews were already asked about - the same "
            "gate failing the same way, a re-run of a script whose failure was reviewed, or a second "
            "diagnostic that reproduces a reviewed defect. A new review would re-ask an answered question."),
        "new-problem": (
            "A defect or a blind reader that the listed reviews do not cover: a new gate, a new operation, a new "
            "stage, or the NEXT failure of a script that was repaired after its review. Buy the review. Choose "
            "this whenever the other two are not clearly true - it is the safe answer and the old behaviour."),
    },
}


def ladder_classify(failure_summary, gate_rows="", recent="", purpose="guard-peer-ladder", n=None):
    """(class, mean probability, spread) for ONE failing run. (None, None, None) when there is no answer."""
    if not failure_summary:
        return None, None, None
    state = {"failure": failure_summary}
    if gate_rows:
        state["gate_rows"] = gate_rows
    if recent:
        state["recent_reviews"] = recent
    mean, spread, err = jev.ask_n(state, {"kind": LADDER_Q}, n=n, purpose=purpose,
                                  timeout=CALL_TIMEOUT, retries=CALL_RETRIES)
    if err or not isinstance(mean, dict) or not mean:
        return None, None, None
    cls = max(mean, key=mean.get)
    return cls, mean[cls], (spread.get("spread") if isinstance(spread, dict) else None)


def ladder_allowed_line(log_name, cls, p, ts):
    """One JSON line per ladder ALLOW, so tools/audit_cycle.py can count builds that ran with no new review."""
    try:
        with open(LADDER_ALLOWED, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": ts, "log": log_name, "class": cls, "p": round(float(p), 4)}) + "\n")
    except OSError:
        pass


def jev_ladder(log_path, failure_text, n=N_RECENT_REVIEWS, before=None, write=True, gate_rows=None):
    """THE LADDER CALL (tools/hooks/guard_peer.py), run BEFORE the ordinary discharge.

    Returns (allow, line):
      allow True  -> release the build now (the line says on which class and probability).
      allow False -> block now; the ordinary discharge has ALREADY been consulted and said no.
      allow None  -> the ladder did not act; the caller runs the old path unchanged.

    NEVER RAISES."""
    try:
        if not jev.get_key():
            return None, None
        fs = jev.summarise_failure(log_path) or jev.normalise(failure_text or "")[:3200]
        if not fs:
            return None, None
        if gate_rows is None:
            try:
                sys.path.insert(0, TOOLS)
                import jev_gaterow
                gate_rows = jev_gaterow.verdicts_for(log_path)
            except Exception:                   # noqa: BLE001 - an advisory input, never a precondition
                gate_rows = ""
        recent_paths = recent_adversary_reviews(n, before=before)
        recent = "\n".join("- %s" % os.path.basename(p) for p in recent_paths)[:1200]
        cls, p, spread = ladder_classify(fs, gate_rows or "", recent)
        if cls is None or p is None:
            return None, None
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        base = os.path.basename(log_path)
        if p < LADDER_P:
            if write:
                gate_log("JEV-LADDER | %s | %s | %s p=%.3f | below %.2f: old path" % (
                    ts, base, cls, p, LADDER_P))
            return None, None
        if cls == "our-script-bug":
            line = "JEV-LADDER | %s | %s | our-script-bug p=%.3f | ALLOW (no machine claim to attack)" % (
                ts, base, p)
            if write:
                gate_log(line)
                ladder_allowed_line(base, cls, p, ts)
            return True, line
        if cls == "already-reviewed-class":
            allow, dline = jev_discharge(log_path, failure_text, n=n, before=before, write=write)
            line = "JEV-LADDER | %s | %s | already-reviewed-class p=%.3f | %s" % (
                ts, base, p, "ALLOW via discharge" if allow else "BLOCK (no citable review)")
            if write:
                gate_log(line)
            if allow:
                return True, (dline or line)
            return False, (dline or line)
        if write:
            gate_log("JEV-LADDER | %s | %s | new-problem p=%.3f | BLOCK (review owed)" % (ts, base, p))
        return None, None                       # the old path runs, exactly as before
    except Exception:                           # noqa: BLE001 - a gate must degrade to its old behaviour
        return None, None


def jev_priorart_dup(step_sentence, n=N_RECENT_REVIEWS, write=True):
    """ADVISORY ONLY (docs/jev-integration-plan.md row #6 'as in A, but do not block'). Returns the advisory
    line when some archived prior-art review scores >= DUP_P for this step, else None. Never raises."""
    try:
        if not jev.get_key() or not step_sentence:
            return None
        cands = sorted(glob.glob(os.path.join(PEER, "*priorart*.md")), key=os.path.getmtime, reverse=True)[:n]
        best = (None, None)
        for rp in cands:
            p, err = answers_step(step_sentence, summarise_review(rp))
            if p is None:
                continue
            if best[0] is None or p > best[0]:
                best = (p, rp)
        if best[0] is not None and best[0] >= DUP_P:
            line = "JEV-PRIORART-DUP | %s | p=%.3f | %s" % (
                time.strftime("%Y-%m-%d %H:%M:%S"), best[0], os.path.basename(best[1]))
            if write:
                gate_log(line)
            return line
        return None
    except Exception:                       # noqa: BLE001
        return None
