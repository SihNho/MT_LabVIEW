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

KINDS = ("cycle", "task", "result", "review", "verdict", "result-line", "next", "goalmap", "decisions-pending")


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
        cited = list(obj.get("advances") or []) + ([obj["unblocks"]] if obj.get("unblocks") else [])
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
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
    fn = {"validate": _cmd_validate, "new": _cmd_new, "result-line": _cmd_result_line, "verdict": _cmd_verdict}
    if a.cmd not in fn:
        ap.print_help()
        return 2
    return fn[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
