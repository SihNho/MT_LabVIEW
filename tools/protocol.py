r"""protocol.py - the session protocol v1 core (docs/session-protocol.md, APPROVED by the user 2026-09-24:
"통신 규약은 … 모든 영역에 JSON 적용하도록 하고 … 목표지도 … 규약 필드 추가 … 사용자 결정도 이렇게 구현하여 적용하도록 하자").

STANDARD LIBRARY ONLY. No LabVIEW, no network.

WHAT EXISTED BEFORE THIS FILE (checked first, CLAUDE.md "check what exists"): no validator, no `docs/protocol/`, no
`tools/bench/cards/`. The log verdict lived as FOUR different text scans - `bgrun.inner_re`, `guard_peer.FAILURE_RE`,
`audit_cycle.FAILURE_RE`, `cycle_runner.GATE_FAIL_RE` - which drifted apart and read quoted prose as failures
(cycles 70, 71, 73). This module replaces them with ONE reading of ONE line (C6).

CLI
    py tools/protocol.py validate <card.json>              exit 0 "OK <schema>" | exit 1 "INVALID <reason>"
    py tools/protocol.py new <kind> --id 74-03 [--force]   skeleton card -> tools/bench/cards/<kind>_<id>.json
    py tools/protocol.py result-line --pass N --fail M [--first-fail TEXT] [--artefact PATH ...]
    py tools/protocol.py verdict <log>                     the C6 verdict of the log's LAST run (JSON)
    py tools/protocol.py bind <task-card>                  C2: a card agent's FIRST command (the hook records it)
    py tools/protocol.py parse-verdict <answer> [--id X] [--out cards/verdict_X.json]    C5
    py tools/protocol.py render-review <review-card>       C4: the card block + verdict contract peer.ps1 sends

IMPORTABLE
    load_card(path) -> dict           (raises ValueError(reason) when invalid)
    validate_obj(obj, goal_ids=None) -> (ok, reason)
    result_line(d) -> "RESULT {...}"  (validated result-line/1)
    parse_result_line(text) -> dict | None      the LAST `RESULT {` line of the text (malformed -> a FAIL dict)
    run_verdict(segment) / log_verdict(text, legacy_re=None, mtime=None) / first_fail_signature(segment, ...)

THE SWITCH (history is not rewritten): a bgrun run segment that carries a RESULT line is judged by it. A segment
WITHOUT one is judged by its exit code alone (`BGRUN END rc=` / `BGRUN TIMEOUT`) - EXCEPT when that run STARTED
before SWITCH_TS, in which case the caller's OLD text rule (`legacy_re`) still applies, so every historical verdict
stays what it was.

AGGREGATION, stated because the draft says "the LAST RESULT line": `parse_result_line` returns the last one, but a run
VERDICT fails when ANY RESULT line printed by that run fails. Reason: a chained command (`motor_gate ...; motor_gate
...`, tools/bench/pi_testmove_20260923e.log) prints one RESULT per step, and the last step passing must not hide an
earlier rejected move. For a single script (stagekit) the two readings coincide: failures only accumulate.
"""
import argparse
import io
import json
import os
import re
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:                                                                   # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA_DIR = os.path.join(ROOT, "docs", "protocol")
CARDS_DIR = os.path.join(HERE, "bench", "cards")
GOALMAP = os.path.join(ROOT, "docs", "goalmap.json")

# THE SWITCH: runs that STARTED before this moment keep their old text-rule verdicts (installed 2026-09-24 by the
# material session that built C6; the bgrun body scan was removed at this time).
SWITCH_TS_TEXT = "2026-09-24 18:25:00"      # the moment tools/bgrun.py stopped scanning bodies (edit landed ~18:24)
SWITCH_TS = time.mktime(time.strptime(SWITCH_TS_TEXT, "%Y-%m-%d %H:%M:%S"))

RESULT_PREFIX = "RESULT "
RESULT_LINE_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
BGRUN_START_RE = re.compile(r"^BGRUN START (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) limit [^\n]*?min:[^\n]*$", re.M)
BGRUN_END_RE = re.compile(r"^BGRUN END rc=(-?\d+)", re.M)
BGRUN_TIMEOUT_RE = re.compile(r"^BGRUN TIMEOUT\b", re.M)
STAGEKIT_GATES_RE = re.compile(r"^=== GATES: (\d+) pass / (\d+) fail(?:; failing: ([^\n]*))?$", re.M)

KINDS = ("cycle", "task", "result", "review", "verdict", "result-line", "next", "goalmap", "decisions-pending", "steer")


# ---------------------------------------------------------------------------------------------------- schemas
def _rel(p):
    """relpath that cannot raise across drives (the guard_cycle.py:518 helper)."""
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def schema_path(schema_name):
    """'task/1' -> docs/protocol/task.json ; a later 'task/2' -> docs/protocol/task.v2.json."""
    m = re.match(r"^([a-z][a-z-]*)/(\d+)$", str(schema_name or ""))
    if not m:
        raise ValueError("schema field %r is not '<name>/<version>'" % (schema_name,))
    name, ver = m.group(1), int(m.group(2))
    return os.path.join(SCHEMA_DIR, name + (".json" if ver == 1 else ".v%d.json" % ver))


_SCHEMAS = {}


def load_schema(schema_name):
    p = schema_path(schema_name)
    if p not in _SCHEMAS:
        if not os.path.exists(p):
            raise ValueError("no schema file for %r (%s)" % (schema_name, _rel(p)))
        with open(p, encoding="utf-8") as f:
            _SCHEMAS[p] = json.load(f)
    return _SCHEMAS[p]


_TYPES = {"string": str, "boolean": bool, "object": dict, "array": list}


def _is_type(v, t):
    if t == "null":
        return v is None
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t])


def _check(v, s, root, path):
    """JSON-Schema subset: $ref(#/definitions/x) type enum const pattern min/maxLength min/maxItems items
    properties required additionalProperties(false) anyOf minimum. Returns None or a one-line reason."""
    if "$ref" in s:
        ref = s["$ref"]
        if not ref.startswith("#/definitions/"):
            return "%s: unsupported $ref %s" % (path, ref)
        return _check(v, root["definitions"][ref.split("/")[-1]], root, path)
    if "anyOf" in s:
        errs = [_check(v, alt, root, path) for alt in s["anyOf"]]
        if all(errs):
            return "%s: matches none of the alternatives (%s)" % (path, " | ".join(e for e in errs))
    if "type" in s:
        ts = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(_is_type(v, t) for t in ts):
            return "%s: expected %s, got %s" % (path, "/".join(ts), type(v).__name__)
    if "const" in s and v != s["const"]:
        return "%s: must be %r, got %r" % (path, s["const"], v)
    if "enum" in s and v not in s["enum"]:
        return "%s: %r not in %s" % (path, v, s["enum"])
    if isinstance(v, str):
        if "minLength" in s and len(v) < s["minLength"]:
            return "%s: shorter than %d chars" % (path, s["minLength"])
        if "maxLength" in s and len(v) > s["maxLength"]:
            return "%s: %d chars > limit %d" % (path, len(v), s["maxLength"])
        if "pattern" in s and not re.search(s["pattern"], v):
            return "%s: %r does not match %s" % (path, v[:60], s["pattern"])
    if isinstance(v, (int, float)) and not isinstance(v, bool) and "minimum" in s and v < s["minimum"]:
        return "%s: %r < minimum %r" % (path, v, s["minimum"])
    if isinstance(v, list):
        if "minItems" in s and len(v) < s["minItems"]:
            return "%s: fewer than %d items" % (path, s["minItems"])
        if "maxItems" in s and len(v) > s["maxItems"]:
            return "%s: %d items > limit %d" % (path, len(v), s["maxItems"])
        if "items" in s:
            for i, x in enumerate(v):
                e = _check(x, s["items"], root, "%s[%d]" % (path, i))
                if e:
                    return e
    if isinstance(v, dict):
        for k in s.get("required", ()):
            if k not in v:
                return "%s: missing required field %r" % (path, k)
        props = s.get("properties", {})
        if s.get("additionalProperties") is False:
            extra = sorted(k for k in v if k not in props)
            if extra:
                return "%s: unknown field(s) %s" % (path, extra)
        for k, sub in props.items():
            if k in v:
                e = _check(v[k], sub, root, "%s.%s" % (path, k))
                if e:
                    return e
    return None


def goal_ids(path=GOALMAP):
    """The ids a card may cite (requirements + milestones), or None when the goal map is absent/unreadable."""
    try:
        with open(path, encoding="utf-8") as f:
            g = json.load(f)
        return {r["id"] for r in g.get("requirements", [])} | {m["id"] for m in g.get("milestones", [])}
    except Exception:                                                               # noqa: BLE001
        return None


def validate_obj(obj, goal_ids=None):
    """(True, 'OK <schema>') or (False, '<one-line reason>'). `goal_ids`: when given, every advances/unblocks/blocks
    id must be one of them (the CLI passes docs/goalmap.json's ids; the self-test passes a fixture)."""
    if not isinstance(obj, dict):
        return False, "top level is %s, not a JSON object" % type(obj).__name__
    try:
        schema = load_schema(obj.get("schema"))
    except ValueError as e:
        return False, str(e)
    err = _check(obj, schema, schema, "$")
    if err:
        return False, err
    if goal_ids is not None:
        cited = (list(obj.get("advances") or []) + ([obj["unblocks"]] if obj.get("unblocks") else [])
                 + list(obj.get("goal_ids") or []))                                     # steer/1

        for it in obj.get("items") or []:
            if isinstance(it, dict):
                cited += list(it.get("blocks") or [])
        unknown = sorted(set(cited) - set(goal_ids))
        if unknown:
            return False, "$: goal-map id(s) %s not in docs/goalmap.json" % unknown
    return True, "OK " + obj["schema"]


def load_card(path, goal_ids=None):
    with open(path, encoding="utf-8") as f:
        try:
            obj = json.load(f)
        except ValueError as e:
            raise ValueError("not JSON: %s" % e)
    ok, why = validate_obj(obj, goal_ids)
    if not ok:
        raise ValueError(why)
    return obj


# ---------------------------------------------------------------------------------------------- C6 RESULT line
def result_line(d):
    """The one-line text form. Validated; ASCII-escaped so a cp949 console can always print it."""
    d = dict(d)
    d.setdefault("schema", "result-line/1")
    ok, why = validate_obj(d)
    if not ok:
        raise ValueError("result_line: " + why)
    return RESULT_PREFIX + json.dumps(d, ensure_ascii=True, separators=(",", ":"))


def make_result(n_pass, n_fail, first_fail=None, artefacts=(), status=None):
    st = status or ("PASS" if (n_fail == 0 and not first_fail) else "FAIL")
    ff = None if first_fail is None else str(first_fail)[:200]
    return {"schema": "result-line/1", "status": st, "gates": {"pass": int(n_pass), "fail": int(n_fail)},
            "first_fail": ff, "artefacts": list(artefacts)}


def _malformed(raw, why):
    return {"schema": "result-line/1", "status": "FAIL", "gates": {"pass": 0, "fail": 1},
            "first_fail": ("malformed RESULT line (%s): %s" % (why, raw))[:200], "artefacts": []}


def all_result_lines(text):
    out = []
    for m in RESULT_LINE_RE.finditer(text or ""):
        raw = m.group(1)
        try:
            d = json.loads(raw)
        except ValueError as e:
            out.append(_malformed(raw, "not JSON: %s" % e))
            continue
        ok, why = validate_obj(d) if isinstance(d, dict) and d.get("schema") == "result-line/1" else (
            False, "schema is not result-line/1")
        out.append(d if ok else _malformed(raw, why))
    return out


def parse_result_line(text):
    """The LAST `RESULT {...}` line of `text` as a dict, or None when there is none. A malformed one is a FAIL."""
    r = all_result_lines(text)
    return r[-1] if r else None


def result_failed(d):
    return d is None or d.get("status") != "PASS" or int((d.get("gates") or {}).get("fail", 1)) > 0


# ----------------------------------------------------------------------------------------- run segments + verdicts
def segments(text):
    """[(start_epoch_or_None, command_line, segment_text)] - one per `BGRUN START`, in file order."""
    marks = list(BGRUN_START_RE.finditer(text or ""))
    out = []
    for i, m in enumerate(marks):
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        try:
            t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            t = None
        out.append((t, m.group(0), text[m.start():stop]))
    return out


def last_segment(text):
    segs = segments(text)
    return segs[-1] if segs else (None, "", text or "")


def run_verdict(segment):
    """C6 verdict of ONE run. failed = any RESULT line fails, or the process ended rc!=0, or TIMEOUT.
    source: 'result' when a RESULT line exists, else 'rc' when an END/TIMEOUT line exists, else 'none' (in flight or
    not a bgrun log)."""
    res = all_result_lines(segment)
    ends = BGRUN_END_RE.findall(segment or "")
    timeout = bool(BGRUN_TIMEOUT_RE.search(segment or ""))
    rc = int(ends[-1]) if ends else None
    bad = [d for d in res if result_failed(d)]
    failed = bool(bad) or timeout or (rc is not None and rc != 0)
    first = None
    if bad:
        first = bad[0].get("first_fail") or "RESULT status=%s gates %s" % (bad[0].get("status"), bad[0].get("gates"))
    elif timeout:
        first = "BGRUN TIMEOUT"
    elif rc:
        first = "BGRUN END rc=%d" % rc
    return {"source": "result" if res else ("rc" if (ends or timeout) else "none"), "failed": failed,
            "first_fail": first, "rc": rc, "timeout": timeout, "results": len(res)}


def is_legacy(start_ts, mtime=None):
    t = start_ts if start_ts is not None else mtime
    return t is not None and t < SWITCH_TS


def log_verdict(text, legacy_re=None, mtime=None):
    """Verdict of the LAST run in a (possibly appended) log. Pre-switch runs without a RESULT line keep the caller's
    old text rule (`legacy_re`, searched over that segment); everything else is run_verdict()."""
    ts, cmd, seg = last_segment(text)
    if not cmd:
        # NOT A bgrun RUN LOG (no BGRUN START: a watchdog `stall_*` record, the Jev journal, a note). C6 governs script
        # runs only; such a file keeps the caller's text rule at any date, and quoted `BGRUN END rc=N` / RESULT lines
        # inside it are never read as a verdict (tools/bench/jev_gate.log quotes `BGRUN END rc=137`).
        m = legacy_re.search(text or "") if legacy_re is not None else None
        return {"source": "no-run", "failed": bool(m), "rc": None, "timeout": False, "results": 0, "start": None,
                "command": "", "first_fail": (text[m.start():].splitlines() or [""])[0].strip()[:200] if m else None}
    v = run_verdict(seg)
    v["start"], v["command"] = ts, cmd
    if v["results"] == 0 and legacy_re is not None and is_legacy(ts, mtime):
        m = legacy_re.search(seg)
        v["source"], v["failed"] = "legacy", bool(m)
        v["first_fail"] = (seg[m.start():].splitlines() or [""])[0].strip()[:200] if m else None
    return v


def first_fail_signature(segment, legacy_re=None, start_ts=None):
    """For cycle_runner's SAME-MISTAKE trigger: the raw first-failure text of ONE run segment, or None.
    RESULT.first_fail when the run printed a RESULT line; the old GATE_FAIL_RE match (group 1 or 2) for a pre-switch
    run without one; None otherwise (an exit code alone names no gate)."""
    bad = [d for d in all_result_lines(segment) if result_failed(d)]
    if bad:
        return bad[0].get("first_fail") or "RESULT FAIL"
    if all_result_lines(segment):
        return None
    if legacy_re is not None and is_legacy(start_ts):
        g = legacy_re.search(segment)
        if g:
            return next((x for x in g.groups() if x), g.group(0))
    return None


def stagekit_result_from_gates(segment):
    """REPLAY ONLY: what stagekit's RESULT line would have been, from its `=== GATES: n pass / m fail` line."""
    m = None
    for m in STAGEKIT_GATES_RE.finditer(segment or ""):
        pass
    if not m:
        return None
    npass, nfail = int(m.group(1)), int(m.group(2))
    first = (m.group(3) or "").split(", ")[0] or None
    return make_result(npass, nfail, first if nfail else None)


# ------------------------------------------------------------------------------ C2 binding + flag enforcement
# MEASURED 2026-09-24 (docs/session-protocol.md, "Binding rule"): a PreToolUse payload from inside a sub-agent carries
# `agent_id` + `agent_type`; the main session's has neither. A card-carrying sub-agent's FIRST command is
# `py tools/protocol.py bind <card>`; the hook (tools/hooks/guard_card.py, called by guard_bash for Bash/PowerShell and
# registered on its own for the other tools) records {agent_id: card} here, and every later call of that agent_id is
# checked against the card's flags. Only the agent types that are DEFINED to take a card are bound; Explore/Plan/
# bench-*/claude-code-guide carry no card and are not governed by this (they are not dispatched with task/1).
ACTIVE = os.environ.get("PROTOCOL_ACTIVE") or os.path.join(CARDS_DIR, "active.json")   # env: self-tests only
CARD_AGENT_TYPES = ("material", "log-reader", "motor-limit-checker")

# The WHOLE command must be the bind call (optionally after `cd <dir> &&`): an unbound agent may run nothing else, so
# `py tools/protocol.py bind x; <anything>` is not a bind.
BIND_CMD_RE = re.compile(
    r"^\s*(?:cd\s+(?:\"[^\"]*\"|'[^']*'|\S+)\s*(?:&&|;)\s*)?"
    r"py(?:thon)?(?:\.exe)?\s+(?:-\S+\s+)*[\"']?(?:[^\s\"'|;&]*[\\/])?tools[\\/]protocol\.py[\"']?\s+bind\s+"
    r"[\"']?([^\s\"'|;&]+)[\"']?\s*$", re.I)

# A script in COMMAND POSITION (after py/python and its flags) - never a path that is only read (`head x.py`, `grep
# y x.py`): measured 2026-09-24, the first version refused `head tools/bench/selftest_stagekit.py` as a LabVIEW run.
# A quoted path may contain spaces (this project lives under "2. Tracking"); an unquoted one may not.
PY_TOKEN_RE = re.compile(r"(?:^|[\s;&|(\"'])py(?:thon)?[\w.]*\s+(?:-[\w-]+\s+)*"
                         r"(?:\"([^\"]*\.py)\"|'([^']*\.py)'|((?:[A-Za-z]:)?[^\s\"'|;&]*\.py))", re.I)
LV_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+(?:gscript|lvclick|stagekit|win32com)\b", re.M)
LV_CMD_RE = re.compile(r"lv_gui\.ps1|LabVIEW\.exe|Stop-Process\s+-Name\s+LabVIEW|import\s+(?:gscript|lvclick)|"
                       r"from\s+(?:gscript|lvclick)", re.I)
RECIPE_PATH_RE = re.compile(r"tools[\\/]recipes[\\/]", re.I)
SAVE_SRC_RE = re.compile(r"\b(?:gscript\.|gs\.)?(?:gui_save|save)\s*\(|SaveInstrument|\.SaveVI\b", re.I)
GUI_STATE_ACTIONS = ("click", "clickprobe", "rclick", "dclick", "drag", "wire", "keys", "key", "activate")  # lv_gui.ps1:669
GUI_ACTION_RE = re.compile(r"lv_gui\.ps1\b[^|;&]*?-Action\s+['\"]?(\w+)", re.I)
GUI_SRC_RE = re.compile(r"\bgui_save\s*\(|['\"]-Action['\"]\s*,\s*['\"](?:%s)['\"]" % "|".join(GUI_STATE_ACTIONS), re.I)
RUN_VI_SRC_RE = re.compile(r"\.Run\(\s*(?:True|False|0|1)?\s*\)")
RUN_VI_CMD_RE = re.compile(r"drive_original_copy", re.I)
GIT_COMMIT_RE = re.compile(r"\bgit\b(?:\s+-\S+(?:\s+\S+)?)*\s+commit\b", re.I)
MOTOR_CMD_RE = re.compile(r"motor_gate\.py|motor_send_pi\.ps1|motor_asi_io\.ps1", re.I)
RUNNER_CMD_RE = re.compile(r"cycle_runner\.py", re.I)
STATUS_WRITE_RE = re.compile(r"(?:>>?|\bSet-Content\b|\bAdd-Content\b|\bOut-File\b|\bsed\s+-i\b|\btee\b|\bmv\b|\bcp\b|"
                             r"\bMove-Item\b|\bCopy-Item\b|os\.replace)[^|;&\n]*?\b(?:STATUS|CLAUDE)\.md\b", re.I)
# peer dispatch -> the role name the card's `peers` list uses (docs/protocol/task.json flags.peers enum)
PEER_SCRIPT_ROLES = (("prior_art_review.py", "priorart"), ("retrospective.py", "retrospective"),
                     ("outcome_review.py", "outcome"), ("doc_ingest.py", "ingest"))


def _norm(p):
    return os.path.normcase(os.path.abspath(p)).replace("\\", "/")


def _glob_re(g):
    """A write-flag glob -> regex over '/'-separated paths. `**/` = any depth incl. none, `**` = anything, `*` = one
    segment, `?` = one char. Relative globs are relative to the project root."""
    g = g.replace("\\", "/")
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif g.startswith("**", i):
            out, i = out + ".*", i + 2
        elif g[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif g[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(g[i]), i + 1
    return re.compile("^" + out + "$", re.I)


def path_in_globs(path, globs):
    ap = _norm(path)
    root = _norm(ROOT)
    rel = ap[len(root) + 1:] if ap.startswith(root + "/") else None
    for g in globs or []:
        gg = g.replace("\\", "/")
        absg = bool(re.match(r"^[A-Za-z]:/|^/", gg))
        target = ap if absg else rel
        if target is not None and _glob_re(_norm(gg) if absg else gg).match(target):
            return True
    return False


def _load_active():
    try:
        with open(ACTIVE, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_active(d):
    os.makedirs(os.path.dirname(ACTIVE), exist_ok=True)
    tmp = ACTIVE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ACTIVE)


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def bind(agent_id, agent_type, card_path, goals="default"):
    """Record the binding. Returns (ok, message). The card must be a VALID task/1."""
    p = _abs(card_path)
    try:
        card = load_card(p, goal_ids() if goals == "default" else goals)
    except (OSError, ValueError) as e:
        return False, "card %s is not a valid task/1: %s" % (card_path, str(e)[:200])
    if card.get("schema") != "task/1":
        return False, "card %s is %s, not task/1" % (card_path, card.get("schema"))
    d = _load_active()
    d[agent_id] = {"card": _rel(p), "agent_type": agent_type, "id": card["id"],
                   "bound": time.strftime("%Y-%m-%d %H:%M:%S"), "md5": _md5(p)}
    _save_active(d)
    return True, "BOUND agent %s (%s) -> %s (id %s)" % (agent_id, agent_type, _rel(p), card["id"])


def binding(agent_id):
    return _load_active().get(agent_id)


def _launched_scripts(cmd):
    """Every `.py` path in the command that exists under the project (resolved against ROOT)."""
    out = []
    for m in PY_TOKEN_RE.finditer(cmd or ""):
        t = next(g for g in m.groups() if g)
        p = _abs(t)
        if os.path.isfile(p):
            out.append(p)
    return out


def code_only(src):
    """The source with COMMENTS and DOCSTRINGS (any bare string statement) blanked, so the flag detectors see calls,
    not prose that mentions them (judgement 2026-09-24, card chat-B2: tools/recipes/build_d1_m3a1.py:95,154,670 only
    MENTION gui_save()). Line numbers are kept. Unparseable source is returned unchanged (fail closed)."""
    import ast
    import tokenize
    try:
        lines = src.splitlines(True)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant)
                    and isinstance(node.value.value, str)):
                for i in range(node.lineno - 1, (node.end_lineno or node.lineno)):
                    lines[i] = "\n"
        text = "".join(lines)
        out = text.splitlines(True)
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                r, c = tok.start
                out[r - 1] = out[r - 1][:c] + "\n"
        return "".join(out)
    except Exception:           # noqa: BLE001
        return src


def _src(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()      # raw: src_features parses it; LV_IMPORT_RE runs on code_only() of it
    except OSError:
        return ""


def peer_role_of(cmd):
    """The review role a command dispatches, or None. peer.ps1: -Role wins, else -Kind (fact/prose), else a
    -Kind review / -Dual = hypothesis."""
    for script, role in PEER_SCRIPT_ROLES:
        if re.search(r"(?:^|[\\/\s\"'])" + re.escape(script), cmd or "", re.I):
            return role
    if not re.search(r"peer\.ps1", cmd or "", re.I):
        return None
    m = re.search(r"-Role\s+['\"]?(\w+)", cmd, re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"-Kind\s+['\"]?(\w+)", cmd, re.I)
    if m and m.group(1).lower() in ("fact", "prose"):
        return m.group(1).lower()
    if re.search(r"-Agent\s+['\"]?claude", cmd, re.I):
        return "audit"
    return "hypothesis"


SAVE_CALLS = {"gui_save", "save", "saveinstrument", "savevi", "save_vi", "save_instrument"}
GUI_CALLS = {"gui_save"}
SHELL_CALLS = {"run", "popen", "call", "check_call", "check_output", "system", "_lv_gui", "lv_gui"}


def _fname(call):
    f = call.func
    return (f.attr if hasattr(f, "attr") else getattr(f, "id", "")) or ""


def _consts(nodes):
    import ast
    return [n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None for n in nodes]


def src_features(src):
    """{'save','gui','run'} for ONE script's source, from its CALLS (judgement 2026-09-24, card chat-B4): a string
    literal that merely contains `gui_save(` or `.Run(` (a self-test fixture, a log quote) triggers nothing.
      save : a call named gui_save / save / SaveInstrument / SaveVI / save_vi / save_instrument
      gui  : a call named gui_save, or an lv_gui invocation with a state-changing action - either `-Action`, <action>
             as consecutive string constants in a call's args or in a list/tuple literal, or a shell call
             (subprocess.run/Popen/..., os.system, _lv_gui) whose string argument reads `lv_gui.ps1 ... -Action <x>`
      run  : a call of an attribute named `Run` (VI.Run(...))
    Regex fallback ONLY on SyntaxError (the old detectors, over code_only())."""
    import ast
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        s = code_only(src)
        return {"save": bool(SAVE_SRC_RE.search(s)), "gui": bool(GUI_SRC_RE.search(s)),
                "run": bool(RUN_VI_SRC_RE.search(s))}
    out = {"save": False, "gui": False, "run": False}

    def action_pair(vals):
        return any(a == "-Action" and (b or "").lower() in GUI_STATE_ACTIONS for a, b in zip(vals, vals[1:]))

    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            name = _fname(n)
            low = name.lower()
            if low in SAVE_CALLS:
                out["save"] = True
            if low in GUI_CALLS:
                out["gui"] = True
            if isinstance(n.func, ast.Attribute) and name == "Run":
                out["run"] = True
            if action_pair(_consts(n.args)):
                out["gui"] = True
            if low in SHELL_CALLS:
                for c in _consts(list(n.args) + [k.value for k in n.keywords]):
                    m = GUI_ACTION_RE.search(c or "")
                    if m and m.group(1).lower() in GUI_STATE_ACTIONS:
                        out["gui"] = True
        elif isinstance(n, (ast.List, ast.Tuple)) and action_pair(_consts(n.elts)):
            out["gui"] = True
    return out


def check_command(card, cmd):
    """None = allowed, else the refusal reason. The card's flags applied to ONE Bash/PowerShell command."""
    fl = card.get("flags") or {}
    cmd = cmd or ""
    scripts = _launched_scripts(cmd)
    srcs = {p: _src(p) for p in scripts}
    if GIT_COMMIT_RE.search(cmd) and not fl.get("git_commit"):
        return "flags.git_commit is false - this card may not `git commit`"
    if not fl.get("status_edit") and STATUS_WRITE_RE.search(cmd):
        return "flags.status_edit is false - this card may not write STATUS.md / CLAUDE.md"
    role = peer_role_of(cmd)
    if role and role not in (fl.get("peers") or []):
        return "flags.peers %s does not include %r - this card may not dispatch that review" % (fl.get("peers"), role)
    if fl.get("hardware", "none") != "gate":
        # INVOKED only (a launched .py, or a .ps1 after & / -File) - `git add tools/cycle_runner.py` is not a run
        # (measured 2026-09-24: the first version refused exactly that commit).
        ran = " ".join(scripts) + " " + " ".join(
            re.findall(r"(?:&|-File)\s+[\"']?([^\s\"']*\.ps1)", cmd, re.I))
        if MOTOR_CMD_RE.search(ran) and not re.search(r"--dry-run|--help", cmd):
            return "flags.hardware is 'none' - motor_gate / motor senders are refused (a --dry-run is allowed)"
        if RUNNER_CMD_RE.search(ran) and not re.search(r"--dry-run|--dry-cmd|--no-motor-hooks", cmd):
            return "flags.hardware is 'none' - a real cycle_runner run opens the motor session; use --dry-run"
    recipes = [p for p in scripts if RECIPE_PATH_RE.search(p)]
    lv_scripts = [p for p in scripts if LV_IMPORT_RE.search(code_only(srcs[p])) or RECIPE_PATH_RE.search(p)]
    feats = {p: src_features(srcs[p]) for p in scripts}
    lv = fl.get("labview", "none")
    if lv == "none" and (LV_CMD_RE.search(cmd) or lv_scripts):
        return "flags.labview is 'none' - this command touches LabVIEW (%s)" % (
            _rel(lv_scripts[0]) if lv_scripts else LV_CMD_RE.search(cmd).group(0))
    if lv == "read":
        if recipes:
            return "flags.labview is 'read' - recipes are refused (%s)" % _rel(recipes[0])
        saving = [p for p in lv_scripts if feats[p]["save"]]
        if saving:
            return "flags.labview is 'read' - %s saves a VI" % _rel(saving[0])
    if not fl.get("gui"):
        m = GUI_ACTION_RE.search(cmd)
        if m and m.group(1).lower() in GUI_STATE_ACTIONS:
            return "flags.gui is false - lv_gui.ps1 -Action %s is state-changing" % m.group(1)
        g = [p for p in scripts if feats[p]["gui"]]
        if g:
            return "flags.gui is false - %s performs state-changing GUI actions" % _rel(g[0])
    if not fl.get("run_vi"):
        if RUN_VI_CMD_RE.search(cmd):
            return "flags.run_vi is false - this command runs a VI (%s)" % RUN_VI_CMD_RE.search(cmd).group(0)
        r = [p for p in scripts if feats[p]["run"]]
        if r:
            return "flags.run_vi is false - %s calls the VI Run method" % _rel(r[0])   # no literal call text here
    return None


def check_write(card, file_path):
    """None = allowed, else the refusal reason, for Edit / Write / NotebookEdit on `file_path`."""
    fl = card.get("flags") or {}
    ap = _norm(file_path)
    for special in ("STATUS.md", "CLAUDE.md"):
        if ap == _norm(os.path.join(ROOT, special)):
            return None if fl.get("status_edit") else "flags.status_edit is false - %s may not be edited" % special
    own = _norm(os.path.join(CARDS_DIR, "result_%s.json" % card.get("id", "")))
    if ap == own:
        return None                      # the card's own result/1 file is always writable
    import tempfile
    tmp = _norm(tempfile.gettempdir())
    if ap.startswith(tmp + "/"):
        return None                      # scratch space (the session's scratchpad lives under %TEMP%)
    if path_in_globs(file_path, fl.get("write") or []):
        return None
    return "flags.write %s does not cover %s" % (fl.get("write"), _rel(file_path))


WRITE_TOOLS = ("Edit", "Write", "NotebookEdit", "MultiEdit")


def hook_decision(payload):
    """The PreToolUse decision for ONE tool call. Returns (allow: bool, message: str|None).
    Main session (no agent_id) and agent types that take no card: always allowed here (the other guards still run)."""
    aid = payload.get("agent_id")
    atype = payload.get("agent_type") or ""
    if not aid or atype not in CARD_AGENT_TYPES:
        return True, None
    tool = payload.get("tool_name") or ""
    ti = payload.get("tool_input") or {}
    cmd = ti.get("command", "") if tool in ("Bash", "PowerShell") else ""
    m = BIND_CMD_RE.match(cmd) if cmd else None
    if m:
        ok, msg = bind(aid, atype, m.group(1))
        return ok, (msg if ok else "BIND REFUSED: " + msg)
    b = binding(aid)
    if not b:
        return False, ("UNBOUND sub-agent (%s %s): this agent's FIRST command must be "
                       "`py tools/protocol.py bind <card>` (docs/session-protocol.md, binding rule). Nothing else "
                       "runs until then." % (atype, aid))
    try:
        card = load_card(_abs(b["card"]), None)
    except (OSError, ValueError) as e:
        return False, "the bound card %s no longer loads: %s" % (b.get("card"), str(e)[:200])
    if tool in ("Bash", "PowerShell"):
        why = check_command(card, cmd)
    elif tool in WRITE_TOOLS:
        why = check_write(card, ti.get("file_path") or ti.get("notebook_path") or "")
    else:
        why = None
    if why:
        return False, "CARD %s (%s): %s" % (card.get("id"), b.get("card"), why)
    return True, None


# ------------------------------------------------------------------------------------------ C4/C5 review/verdict
VERDICT_LINE_RE = re.compile(r"^\s*`{0,3}\s*VERDICT\s+(\{.*\})\s*`{0,3}\s*$", re.M)
ROLE_VERDICTS = {
    "hypothesis": "refuted | supported | unverified",
    "priorart": "novel | settled-already",
    "fact": "supported | refuted | unverified",
    "outcome": "none (no outcome violation) | refuted (the work did not move the deliverable)",
    "retrospective": "none (no violation) | refuted (a structural fault; name it in violations)",
    "ingest": "none (no contradiction) | refuted (contradictions found; count them in note)",
}


def review_card(role, rid, claim, predicted="", observed="", ruled_out=(), attachments=(), note=""):
    """Build + validate a review/1 card; returns the dict. `attachments` = paths (md5 filled in when the file exists)."""
    rid = re.sub(r"[^A-Za-z0-9_.-]", "-", str(rid))[:41].strip("-_.") or "review"
    atts = []
    for a in attachments:
        p = _abs(a)
        atts.append({"path": _rel(p), "md5": _md5(p) if os.path.isfile(p) else None})
    d = {"schema": "review/1", "id": rid, "role": role, "claim": str(claim)[:300], "predicted": str(predicted)[:300],
         "observed": str(observed)[:300], "ruled_out": [str(x)[:200] for x in list(ruled_out)[:3]],
         "attachments": atts, "ask": "refute"}
    if note:
        d["note"] = str(note)[:300]
    ok, why = validate_obj(d)
    if not ok:
        raise ValueError("review_card: " + why)
    return d


def write_review_card(d):
    os.makedirs(CARDS_DIR, exist_ok=True)
    p = os.path.join(CARDS_DIR, "review_%s.json" % d["id"])
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return p


def render_review(card):
    """The review/1 card as the text block peer.ps1 puts in front of the task, plus the verdict/1 contract."""
    lines = ["--- REVIEW CARD (review/1, id %s, role %s) ---" % (card["id"], card["role"]),
             "CLAIM: " + card["claim"]]
    if card.get("predicted"):
        lines.append("PREDICTED: " + card["predicted"])
    if card.get("observed"):
        lines.append("OBSERVED: " + card["observed"])
    for r in card.get("ruled_out") or []:
        lines.append("ALREADY RULED OUT: " + r)
    for a in card.get("attachments") or []:
        lines.append("ATTACHMENT: %s (md5 %s)" % (a["path"], a.get("md5")))
    lines.append("--- END REVIEW CARD ---")
    return "\n".join(lines) + "\n"


def verdict_contract(card):
    allowed = ROLE_VERDICTS.get(card["role"], "refuted | supported | unverified")
    return ("\n\n--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---\n"
            "Write your answer as usual. Then make the LAST line of your answer exactly one line of the form\n"
            "VERDICT {\"schema\":\"verdict/1\",\"id\":\"%s\",\"verdict\":\"<one of: %s>\",\"alternative\":\"...\","
            "\"discriminating_test\":\"...\",\"violations\":[],\"sources\":[\"url or file:line\"],\"note\":\"\"}\n"
            "Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 "
            "items {\"slug\",\"loss_min\",\"loss_usd\",\"evidence\"} using the retrospective slug list. Gates read "
            "ONLY this line; the prose above it is archived for people.\n" % (card["id"], allowed))


def parse_verdict(text, want_id=None):
    """(dict, None) for the LAST valid `VERDICT {...}` line of the answer, else (None, reason)."""
    ms = list(VERDICT_LINE_RE.finditer(text or ""))
    if not ms:
        return None, "no VERDICT line"
    raw = ms[-1].group(1)
    try:
        d = json.loads(raw)
    except ValueError as e:
        return None, "VERDICT line is not JSON: %s" % e
    ok, why = validate_obj(d)
    if not ok:
        return None, why
    if want_id and d.get("id") != want_id:
        return None, "VERDICT id %r != review id %r" % (d.get("id"), want_id)
    return d, None


# ------------------------------------------------------------------------------------- C7 next.json / decisions
NEXT_JSON = os.path.join(HERE, "bench", "next.json")
DECISIONS = os.path.join(HERE, "bench", "decisions_pending.json")


def next_state(path=NEXT_JSON):
    """(md5_of_bytes | 'absent', card | None, reason | None) - the runner's and next_gate's single reading."""
    if not os.path.exists(path):
        return "absent", None, "no next.json"
    m = _md5(path)
    try:
        return m, load_card(path, goal_ids()), None
    except (OSError, ValueError) as e:
        return m, None, str(e)[:200]


def open_decisions(path=DECISIONS):
    try:
        d = load_card(path, None)
    except (OSError, ValueError):
        return []
    return [it for it in d.get("items", []) if it.get("status") == "open"]


# ------------------------------------------------------------------------------ steer/1 (outcome-review steering)
# User 2026-09-24 ("아웃컴 리뷰에 조향카드 부여하는 것 동의"; decisions_pending D-2026-09-24-02 "yes as proposed: steering
# card, two refusals stop the runner"). outcome_review.py writes the card when a verdict REPEATS; cycle_runner.py carries
# the active one in cycle/1 `steer` and reads the judgement's answer from next/1 `steer` after the cycle.
STEER_STATE = os.path.join(HERE, "bench", "steer_state.json")
STEER_REFUSALS_STOP = 2
OUTCOME_SLUGS = ("goal-requirement-not-advanced", "tooling-over-delivery", "product-not-runnable", "ordering-stale",
                 "decision-starved", "scope-inflation", "measurement-without-product")
OUTCOME_LINE_RE = re.compile(r"^\s*OUTCOME-VIOLATION:\s*([a-z][a-z-]*)\s*$", re.M)
STEER_ACTS = {    # mechanical, one per slug; {active}/{open} are filled from docs/goalmap.json
    "product-not-runnable": "The next act RUNS or produces a runnable deliverable for an active milestone ({active}).",
    "goal-requirement-not-advanced": "The next act advances an open requirement ({open}) through an active milestone.",
    "tooling-over-delivery": "No tooling/device/doc work as the next act: it is a deliverable build or run.",
    "ordering-stale": "Re-order against docs/goalmap.json: the next act advances an active milestone ({active}).",
    "decision-starved": "Every user question the work waits on goes to decisions_pending.json this cycle.",
    "scope-inflation": "The next act is inside an active milestone's done_when ({active}); nothing outside it.",
    "measurement-without-product": "The next act changes the product (a VI build or run), not only a measurement.",
}


def outcome_slugs(md_text):
    """The OUTCOME-VIOLATION slugs of an archived outcome review's ANSWER (after `## Answer`, before `## What was
    done with it`) - the question echo carries the template lines and must not count."""
    t = md_text or ""
    i = t.find("\n## Answer")
    body = t[i:] if i >= 0 else t
    j = body.find("\n## What was done with it")
    body = body[:j] if j >= 0 else body
    return sorted({s for s in OUTCOME_LINE_RE.findall(body) if s in OUTCOME_SLUGS})


def current_cycle(cards_dir=CARDS_DIR):
    """The highest n of `cycle_<n>.json` in the cards dir (0 when none)."""
    n = 0
    try:
        for fn in os.listdir(cards_dir):
            m = re.match(r"^cycle_(\d+)\.json$", fn)
            if m:
                n = max(n, int(m.group(1)))
    except OSError:
        pass
    return n


def steer_for(latest, previous, cycle, goalmap_path=GOALMAP):
    """(steer/1 card | None, why). A card only when a slug appears in BOTH reviews (a REPEATED verdict)."""
    def rd(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    a, b = outcome_slugs(rd(latest)), outcome_slugs(rd(previous))
    rep = sorted(set(a) & set(b))
    if not rep:
        return None, "no repeated verdict (latest %s, previous %s)" % (a or ["none"], b or ["none"])
    try:
        with open(goalmap_path, encoding="utf-8") as f:
            gm = json.load(f)
    except (OSError, ValueError):
        gm = {}
    active = [m["id"] for m in gm.get("milestones", []) if m.get("status") == "active"]
    open_r = [r["id"] for r in gm.get("requirements", []) if r.get("status") in ("open", "moving")]
    ids = list(active) + ([r for r in open_r] if "goal-requirement-not-advanced" in rep else [])
    ids = ids or [m["id"] for m in gm.get("milestones", []) if m.get("status") != "done"][:1]
    act = " ".join(STEER_ACTS[s].format(active=", ".join(active) or "-", open=", ".join(open_r) or "-") for s in rep)
    card = {"schema": "steer/1", "cycle": int(cycle), "item": "outcome:" + "+".join(rep), "verdicts": rep,
            "required_act": act[:600], "goal_ids": ids,
            "evidence": [{"path": _rel(latest), "md5": _md5(latest)}, {"path": _rel(previous), "md5": _md5(previous)}],
            "note": "repeated outcome verdict; follow it in next.json `steer`, or refuse it there with evidence"}
    ok, why = validate_obj(card, {r.get("id") for r in gm.get("requirements", [])} |
                           {m.get("id") for m in gm.get("milestones", [])} if gm else None)
    return (card, "repeated: %s" % rep) if ok else (None, "steer card invalid: " + why)


def write_steer(card, cards_dir=CARDS_DIR):
    os.makedirs(cards_dir, exist_ok=True)
    p = os.path.join(cards_dir, "steer_%d.json" % card["cycle"])
    with open(p, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    return p


def _json_load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _json_save(p, obj):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def active_steer(cards_dir=CARDS_DIR, state_path=STEER_STATE):
    """(path, card) of the newest VALID steer card that is not closed (followed / stopped) in the state file, or
    (None, None). A newer card for an item re-opens it with a fresh refusal count."""
    cands = []
    try:
        for fn in os.listdir(cards_dir):
            m = re.match(r"^steer_(\d+)\.json$", fn)
            if m:
                cands.append((int(m.group(1)), os.path.join(cards_dir, fn)))
    except OSError:
        return None, None
    st = _json_load(state_path, {}).get("items", {})
    for _n, p in sorted(cands, reverse=True):
        try:
            card = load_card(p, None)
        except (OSError, ValueError):
            continue
        rec = st.get(card["item"]) or {}
        if _norm(rec.get("card", "")) == _norm(p) and rec.get("status") in ("followed", "stopped"):
            return None, None          # the newest card was already answered; older ones are superseded
        return p, card
    return None, None


def steer_after_cycle(steer_path, steer_card, next_card, n, state_path=STEER_STATE):
    """Read the judgement's answer (next/1 `steer`) to the steer carried in cycle n. Returns (action, detail):
    'followed' | 'refused' | 'stop'. No answer, or an answer for another item, counts as a refusal."""
    item = steer_card["item"]
    state = _json_load(state_path, {})
    items = state.setdefault("items", {})
    rec = items.get(item)
    if not rec or _norm(rec.get("card", "")) != _norm(steer_path):
        rec = {"card": _rel(steer_path), "status": "open", "refusals": []}
    reply = (next_card or {}).get("steer") if isinstance(next_card, dict) else None
    if reply and reply.get("item") == item and reply.get("response") == "follow":
        rec.update(status="followed", followed_cycle=n)
        items[item] = rec
        _json_save(state_path, state)
        return "followed", "cycle %d follows %s" % (n, item)
    if reply and reply.get("item") == item:
        why = "refused with evidence %s" % reply.get("evidence")
    elif reply:
        why = "answered another item %r" % reply.get("item")
    else:
        why = "no steer answer in next.json" if next_card is not None else "next.json absent/invalid"
    rec["refusals"].append({"cycle": n, "why": why[:200]})
    action = "stop" if len(rec["refusals"]) >= STEER_REFUSALS_STOP else "refused"
    if action == "stop":
        rec["status"] = "stopped"
    items[item] = rec
    _json_save(state_path, state)
    return action, "cycle %d: %s (%d/%d)" % (n, why, len(rec["refusals"]), STEER_REFUSALS_STOP)


def add_steer_decision(steer_card, n, refusals, path=DECISIONS):
    """Append ONE open decisions-pending/1 item for a steer refused twice; validate the whole file before writing.
    Returns (id, None) or (None, reason)."""
    d = _json_load(path, {"schema": "decisions-pending/1", "items": []})
    items = d.setdefault("items", [])
    day = time.strftime("%Y-%m-%d")
    seq = 1 + sum(1 for it in items if str(it.get("id", "")).startswith("D-%s-" % day))
    did = "D-%s-%02d" % (day, seq)
    q = ("Steering card %s (%s) was refused twice by the judgement sessions (%s). Follow it, or withdraw it?"
         % (steer_card["item"], steer_card["required_act"][:90], "; ".join(r.get("why", "")[:40] for r in refusals)))
    items.append({"id": did, "asked": time.strftime("%Y-%m-%dT%H:%M"), "by": "cycle %d" % n, "question": q[:300],
                  "options": ["follow the steer", "withdraw the steer", "discuss"], "recommendation": None,
                  "blocks": [g for g in steer_card.get("goal_ids", []) if g.startswith("M")], "status": "open",
                  "answer": None, "answered_at": None})
    ok, why = validate_obj(d)
    if not ok:
        return None, why
    _json_save(path, d)
    return did, None


# ------------------------------------------------------------------------------------------------- skeletons + CLI
SKELETONS = {
    "task": {"schema": "task/1", "id": "", "kind": "build", "goal": "", "why": "", "inputs": [], "pass": [],
             "outputs": [], "flags": {"labview": "none", "gui": False, "hardware": "none", "run_vi": False,
                                      "write": [], "status_edit": False, "git_commit": False, "peers": []},
             "budget": {"failures": 2, "minutes": 60}, "rules": [], "advances": []},
    "result": {"schema": "result/1", "id": "", "status": "FAIL", "gates": {"pass": 0, "fail": 0}, "first_fail": None,
               "blocked_by": None, "artefacts": [], "facts": [], "open": [],
               "cost": {"usd": None, "minutes": None, "labview_runs": 0}, "note": ""},
    "review": {"schema": "review/1", "id": "", "role": "hypothesis", "claim": "", "predicted": "", "observed": "",
               "ruled_out": [], "attachments": [], "ask": "refute"},
    "verdict": {"schema": "verdict/1", "id": "", "verdict": "none", "alternative": "", "discriminating_test": "",
                "violations": [], "sources": [], "note": ""},
    "next": {"schema": "next/1", "cycle": 0, "act": "", "task_kind": "build", "plan": None, "pass": [],
             "blocked_by": None, "stop_requested": False, "advances": [], "note": ""},
    "cycle": {"schema": "cycle/1", "cycle": 0, "rig_state": "unknown", "model": "claude-opus-5-5", "effort": "medium",
              "firefighter": None, "bed": None, "errorlist": None, "motor_session": None,
              "next": "tools/bench/next.json", "budget": {"minutes": 180, "dispatches": 8}, "rules": []},
    "decisions-pending": {"schema": "decisions-pending/1", "items": []},
    "result-line": make_result(0, 0),
}


def _cmd_validate(a):
    try:
        load_card(a.file, None if a.no_goalmap else goal_ids())
    except (OSError, ValueError) as e:
        print("INVALID %s: %s" % (a.file, str(e).replace("\n", " ")[:300]))
        return 1
    with open(a.file, encoding="utf-8") as f:
        print("OK %s %s" % (json.load(f)["schema"], a.file))
    return 0


def _cmd_new(a):
    if a.kind not in SKELETONS:
        print("unknown kind %r; one of %s" % (a.kind, sorted(SKELETONS)))
        return 1
    card = json.loads(json.dumps(SKELETONS[a.kind]))
    if "id" in card:
        card["id"] = a.id
    if a.kind in ("next", "cycle") and re.match(r"^\d+", a.id):
        card["cycle"] = int(re.match(r"^\d+", a.id).group(0))
    os.makedirs(CARDS_DIR, exist_ok=True)
    out = os.path.join(CARDS_DIR, "%s_%s.json" % (a.kind, a.id))
    if os.path.exists(out) and not a.force:
        print("EXISTS %s (use --force)" % _rel(out))
        return 1
    with open(out, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    print("WROTE %s (skeleton - fill it, then `validate`)" % _rel(out))
    return 0


def _md5(p):
    import hashlib
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _cmd_result_line(a):
    arts = [{"path": p, "md5": _md5(p) if os.path.isfile(p) else None} for p in (a.artefact or [])]
    print(result_line(make_result(a.pass_, a.fail, a.first_fail, arts)))
    return 0


def _cmd_verdict(a):
    with open(a.log, encoding="utf-8", errors="replace") as f:
        text = f.read()
    v = log_verdict(text, mtime=os.path.getmtime(a.log))
    print(json.dumps(v, ensure_ascii=True))
    return 1 if v["failed"] else 0


def _cmd_bind(a):
    """The CLI half of the binding: validates the card and reports whether the HOOK recorded it. The binding itself
    is written by the PreToolUse hook, which is the only process that sees the caller's agent_id."""
    p = _abs(a.card)
    try:
        card = load_card(p, goal_ids())
    except (OSError, ValueError) as e:
        print("INVALID %s: %s" % (a.card, str(e)[:300]))
        return 1
    held = [aid for aid, b in _load_active().items() if _norm(_abs(b.get("card", ""))) == _norm(p)]
    if held:
        print("BOUND %s (id %s) to agent(s) %s" % (_rel(p), card["id"], ", ".join(held)))
    else:
        print("VALID %s (id %s) - no binding recorded (main session, or the hook is not installed)" % (_rel(p), card["id"]))
    return 0


def _cmd_parse_verdict(a):
    with open(a.file, encoding="utf-8", errors="replace") as f:
        d, why = parse_verdict(f.read(), a.id or None)
    if d is None:
        print("NO-VERDICT: %s" % why)
        return 1
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    print("VERDICT-CARD %s verdict=%s%s" % (d["id"], d["verdict"], (" -> " + _rel(a.out)) if a.out else ""))
    return 0


def _cmd_render_review(a):
    try:
        card = load_card(_abs(a.card), None)
    except (OSError, ValueError) as e:
        print("INVALID %s: %s" % (a.card, str(e)[:300]))
        return 1
    if card.get("schema") != "review/1":
        print("INVALID: %s is not review/1" % a.card)
        return 1
    parts = {"card": render_review(card), "contract": verdict_contract(card)}
    sys.stdout.write(parts[a.part] if a.part in parts else parts["card"] + parts["contract"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("bind")
    b.add_argument("card")
    pv = sub.add_parser("parse-verdict")
    pv.add_argument("file")
    pv.add_argument("--id", default="")
    pv.add_argument("--out", default="")
    rr = sub.add_parser("render-review")
    rr.add_argument("card")
    rr.add_argument("--part", choices=("card", "contract", "both"), default="both")
    v = sub.add_parser("validate")
    v.add_argument("file")
    v.add_argument("--no-goalmap", action="store_true", help="do not check advances/unblocks ids against the goal map")
    n = sub.add_parser("new")
    n.add_argument("kind")
    n.add_argument("--id", required=True)
    n.add_argument("--force", action="store_true")
    r = sub.add_parser("result-line")
    r.add_argument("--pass", dest="pass_", type=int, required=True)
    r.add_argument("--fail", type=int, required=True)
    r.add_argument("--first-fail", default=None)
    r.add_argument("--artefact", action="append")
    d = sub.add_parser("verdict")
    d.add_argument("log")
    a = ap.parse_args(argv)
    fn = {"validate": _cmd_validate, "new": _cmd_new, "result-line": _cmd_result_line, "verdict": _cmd_verdict,
          "bind": _cmd_bind, "parse-verdict": _cmd_parse_verdict, "render-review": _cmd_render_review}
    if a.cmd not in fn:
        ap.print_help()
        return 2
    return fn[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
