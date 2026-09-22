r"""jev_preflight.py - insertion #3 of the SECOND WAVE table in docs/jev-integration-plan.md: PRE-FLIGHT.

    py tools/jev_preflight.py tools/recipes/stage_d1_m3a3_rowD.py

STATIC FIRST, MODEL SECOND. Five mechanical checks run with no network and no model; their results are then
handed, with the script's first 120 lines, to ONE Jev choice: ready / wrong-input / missing-guard / oversized.
The static findings are the evidence; the class is the summary. ADVISORY ONLY - nothing here blocks a launch,
and tools/hooks/guard_bash.py discards the line's value.

THE FIVE CHECKS
  P1 imports `stagekit`                  - CLAUDE.md, 2026-09-22: every new stage/diagnostic is a <=120-line
                                           file on the kit
  P2 input VI                            - every `claudeDev\...vi` literal in the script, and whether it is
                                           named in STATUS.md's `## NEXT` (the bed the hand-off points at)
  P3 uid literals                        - every 4-6 digit integer literal, and whether it appears in ANY
                                           measured JSON under tools/bench (an address nobody measured is the
                                           defect that cost cycles 60 and 84)
  P4 save route stated                   - the script says how the artefact is saved
  P5 `%`-format arity                    - reused from tools/bench/c60c_astcheck.py:percent_format_sites(),
                                           the measured checker; NOT re-implemented

PRIOR ART CHECKED before writing: tools/bench/c60c_astcheck.py (owns the AST gates - imported, not copied);
tools/stagekit.py (the stage skeleton P1 looks for); tools/jev.py (transport); tools/jev_drift.py (the sibling
advisory, whose logging shape this copies). No LabVIEW, no COM.
"""
import ast
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402

STATUS = os.path.join(ROOT, "STATUS.md")
GATE_LOG = os.path.join(BENCH, "jev_gate.log")
HEAD_LINES = 120
OVERSIZE_LINES = 200

NEXT_SECTION_RE = re.compile(r"^##\s+NEXT\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
VI_RE = re.compile(r"[\w\\/. ]*claudeDev[\\/]+([\w.\-]+\.vi)", re.I)
VI_ANY_RE = re.compile(r"([\w.\-]+\.vi)", re.I)
UID_RE = re.compile(r"(?<![\w.])(\d{4,6})(?![\w.])")
SAVE_RE = re.compile(r"\b(?:g\.save|stage\.save|\.save\s*\(|save_as|Save Instrument|gui_save|SAVE_AS|"
                     r"save_path|out_vi|OUT_VI)\b")

PREFLIGHT_Q = {
    "type": "choice",
    "instructions": (
        "`head` is the first 120 lines of a stage or diagnostic script in a LabVIEW VI-scripting project - its "
        "docstring, prediction contract, inputs and the start of its body. `checks` is the result of five "
        "mechanical pre-flight checks already run on the WHOLE file. Decide which ONE of the four applies "
        "before the script is launched. Judge only what would stop this run from producing its artefact; a "
        "gate that may fail on a genuine measurement is not a defect of the script."),
    "criteria": {
        "ready": ("Nothing in the head or the checks would waste the run: the inputs are named and current, "
                  "the addresses are measured ones, the save route is stated, and the file is of a size the "
                  "project's rules allow."),
        "wrong-input": ("The script starts from the wrong file: an input VI that does not exist, or one that "
                        "is not the bed the hand-off names, so the run would build on a superseded artefact."),
        "missing-guard": ("An input or address is not backed by a measurement, or there is no stated save "
                          "route or junk purge, or a `%`-format site would raise before the work is reached - "
                          "a defect a guard would have caught."),
        "oversized": ("The file is a large free-standing script (over 200 lines and not built on the shared "
                      "`stagekit` skeleton), so it cannot be checked before it runs and a late failure throws "
                      "the whole run away."),
    },
}


# ---------------------------------------------------------------------------------------------------- checks
def _next_text():
    try:
        with open(STATUS, encoding="utf-8", errors="replace") as fh:
            m = NEXT_SECTION_RE.search(fh.read())
        return m.group(1) if m else ""
    except OSError:
        return ""


def _claudedev():
    """The claudeDev directory this project saves derived VIs into, from gscript's ONE definition."""
    if getattr(_claudedev, "_cache", None) is not None:
        return _claudedev._cache
    # READ, never IMPORT: gscript is the COM client, and this function runs inside a PreToolUse hook on
    # ordinary commands. Importing it there to learn a directory name would put LabVIEW's client on the path
    # of every shell command in the session.
    d = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
    try:
        with open(os.path.join(HERE, "gscript.py"), encoding="utf-8", errors="replace") as fh:
            m = re.search(r"^CLAUDEDEV\s*=\s*r?[\"'](.+?)[\"']\s*$", fh.read(), re.M)
        if m:
            d = m.group(1)
    except OSError:
        pass
    _claudedev._cache = d
    return d


def _vi_exists(name):
    d = _claudedev()
    try:
        return bool(d) and os.path.exists(os.path.join(d, name))
    except OSError:
        return False


def _measured_uids():
    """Every 4-6 digit integer token appearing in any JSON under tools/bench (cached per process)."""
    if getattr(_measured_uids, "_cache", None) is not None:
        return _measured_uids._cache
    seen = set()
    try:
        names = sorted(n for n in os.listdir(BENCH) if n.lower().endswith(".json"))
    except OSError:
        names = []
    for n in names:
        p = os.path.join(BENCH, n)
        try:
            if os.path.getsize(p) > 8 << 20:
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                seen.update(UID_RE.findall(fh.read()))
        except OSError:
            continue
    _measured_uids._cache = seen
    return seen


def _percent_sites(tree, path):
    """(n_mismatch, n_invalid, detail) from c60c_astcheck's measured checker, or (None, None, why)."""
    argv = sys.argv[:]
    try:
        sys.argv = [os.path.join(BENCH, "c60c_astcheck.py")]      # it parses argv at import time
        if BENCH not in sys.path:
            sys.path.insert(0, BENCH)
        import c60c_astcheck
    except Exception as e:        # noqa: BLE001 - a missing checker must not stop the pre-flight
        return None, None, "c60c_astcheck unavailable: %s" % type(e).__name__
    finally:
        sys.argv = argv
    try:
        mism, _unres, _ver, _ass, invalid, _bytes = c60c_astcheck.percent_format_sites(tree, path)
    except Exception as e:        # noqa: BLE001
        return None, None, "percent_format_sites raised %s" % type(e).__name__
    detail = "; ".join((mism + invalid)[:2])[:220]
    return len(mism), len(invalid), detail


def static_checks(path):
    """The five checks. Returns (dict of results, list of one-line findings). Never raises."""
    res, findings = {}, []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except OSError as e:
        return {"error": str(e)}, ["P0 the script could not be read: %s" % e]
    lines = src.splitlines()
    res["lines"] = len(lines)

    # P1 stagekit
    res["stagekit"] = bool(re.search(r"^\s*(?:import\s+stagekit|from\s+stagekit\s+import)", src, re.M))
    res["oversize"] = (res["lines"] > OVERSIZE_LINES and not res["stagekit"])
    findings.append("P1 stagekit=%s, %d lines%s" % (
        res["stagekit"], res["lines"], "  -> OVERSIZE (>200 and not on the kit)" if res["oversize"] else ""))

    # P2 input VI vs STATUS NEXT
    nxt = _next_text()
    vis = []
    for m in VI_RE.finditer(src):
        if m.group(1) not in vis:
            vis.append(m.group(1))
    if not vis:
        for m in VI_ANY_RE.finditer(src):
            if m.group(1) not in vis:
                vis.append(m.group(1))
    next_vis = sorted({m.group(1) for m in VI_RE.finditer(nxt)})
    named = [v for v in vis if v in next_vis]
    unnamed = [v for v in vis if v not in next_vis]
    res["input_vis"], res["next_vis"] = vis[:8], next_vis[:8]
    res["input_in_next"] = bool(named)
    # EXISTENCE IS REPORTED BESIDE THE NAMING, because they answer different questions and only the first is
    # timeless: STATUS's NEXT says what the CURRENT cycle starts from, so a script written two cycles ago names
    # a bed that was right then and is absent from today's hand-off. Without this line the check would call
    # every older script wrong-input.
    present, absent = [], []
    for v in vis:
        (present if _vi_exists(v) else absent).append(v)
    res["vis_present"], res["vis_absent"] = present[:6], absent[:6]
    findings.append("P2 VI literals %s; named in today's STATUS NEXT: %s; not named: %s; "
                    "present under claudeDev: %s; NOT ON DISK: %s" % (
                        vis[:4] or "-", named[:4] or "-", unnamed[:4] or "-",
                        present[:4] or "-", absent[:4] or "-"))

    # P3 uid literals vs measured JSON
    uids, measured = sorted(set(UID_RE.findall(src))), _measured_uids()
    unmeasured = [u for u in uids if u not in measured]
    res["n_uids"], res["n_unmeasured"] = len(uids), len(unmeasured)
    res["unmeasured"] = unmeasured[:10]
    findings.append("P3 %d uid-shaped literals, %d appear in NO measured tools/bench JSON: %s" % (
        len(uids), len(unmeasured), unmeasured[:6] or "-"))

    # P4 save route
    res["save_route"] = bool(SAVE_RE.search(src))
    findings.append("P4 a save route is stated: %s" % res["save_route"])

    # P5 %-format arity
    try:
        tree = ast.parse(src)
        res["parses"] = True
    except SyntaxError as e:
        res["parses"] = False
        findings.append("P5 the file does NOT parse: %s" % e)
        return res, findings
    nm, ni, detail = _percent_sites(tree, path)
    res["pct_mismatch"], res["pct_invalid"] = nm, ni
    findings.append("P5 %%-format: %s mismatched, %s invalid%s" % (
        nm, ni, ("  [%s]" % detail) if detail else ""))
    return res, findings


# ------------------------------------------------------------------------------------------------- the model
def classify(path, timeout=25, retries=0, purpose="preflight"):
    """(cls, p, findings, res, err). ONE Jev choice over the head + the static findings."""
    res, findings = static_checks(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = "".join([next(fh, "") for _ in range(HEAD_LINES)])
    except OSError as e:
        return None, None, findings, res, str(e)
    state = {"script": os.path.basename(path), "head": head[:9000], "checks": "\n".join(findings)[:2000]}
    resp, err = jev.ask(state, {"preflight": PREFLIGHT_Q}, purpose=purpose, timeout=timeout, retries=retries)
    if err:
        return None, None, findings, res, err
    cls, probs = jev.choice(resp, "preflight")
    p = None
    if isinstance(probs, dict) and cls in probs:
        try:
            p = float(probs[cls])
        except (TypeError, ValueError):
            p = None
    return cls, p, findings, res, None


def line_for(path, timeout=25):
    """The one-line advisory, or None. Never raises."""
    try:
        cls, p, findings, _res, err = classify(path, timeout=timeout)
        if err or not cls:
            return None
        return "JEV-PREFLIGHT | %s | %s p=%s | %s" % (
            os.path.basename(path), cls, ("%.2f" % p) if p is not None else "?",
            " ".join(f.split("  ")[0] for f in findings)[:220])
    except Exception:       # noqa: BLE001
        return None


def advisory(script_path, write_log=True):
    """The hook entry point: print and log one line for a recipe/stage launch. Returns the line or None."""
    try:
        line = line_for(script_path)
        if not line:
            return None
        sys.stderr.write(line + "  (advisory, nothing is blocked; docs/jev-integration-plan.md 2nd wave #3)\n")
        if write_log:
            try:
                with open(GATE_LOG, "a", encoding="utf-8") as fh:
                    fh.write("%s | %s | preflight\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), line))
            except OSError:
                pass
        return line
    except Exception:       # noqa: BLE001
        return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__.strip().splitlines()[2])
        return 2
    path = argv[0]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    cls, p, findings, _res, err = classify(path)
    for f in findings:
        print("  " + f)
    if err:
        print("JEV-PREFLIGHT | %s | (no reading: %s)" % (os.path.basename(path), err[:80]))
        return 0
    print("JEV-PREFLIGHT | %s | %s p=%s | %s" % (
        os.path.basename(path), cls, ("%.2f" % p) if p is not None else "?",
        " ".join(f.split("  ")[0] for f in findings)[:220]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
