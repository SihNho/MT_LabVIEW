# ---
# labview: none
# hardware: none
# ---
"""PostToolUse hook (Write | Edit | MultiEdit | NotebookEdit): check what was just WRITTEN, in the same turn, in seconds.

Card chat-E3 (user 2026-10-04: "에러 잡는 훅도 만들어줘" - "초장에 에러 발생을 극소화하여 시간 낭비를 최소화"). Measured basis:
cycles 142-143 lost ~44 min to errors that were knowable within seconds of writing the file (a plan field over its
schema length, a release line with the wrong slug, a copy of a pair another card had changed, a script that did not
import). The write already happened (PostToolUse cannot undo it); exit 2 hands the problem back to the writing agent
immediately, before it launches anything.

Checked, by path:
  tools/**/*.py|.ps1       scope header present + valid (tools/scope_header.py), compiles / parses, HONEST (a
                           `labview: none` that imports a LabVIEW/COM client, starts a recipe, names lv_gui.ps1 ...),
                           and no OPEN card (task_<id>.json without result_<id>.json) pins this file at another md5
  *.json with a known `schema` (task/1, result/1, stageplan/1, release/1, next/1, ...)
                           protocol.validate_obj (types, enums, maxLength - prose fields included: their LENGTH is
                           schema, their TEXT is never gated); task/1 inputs' md5 == disk; open-card pins as above
  archive/peer/*priorart*.md every FIXED:/REFUTED: line names one of THIS review's verdict slugs and validates
                           (guard_cycle.released_slugs) - 143-1 lost a launch to a review-slug release line
Never refuses anything else; a crash of this hook prints nothing and exits 0 (it must not wedge writing).
Self-test: tools/bench/selftest_c_e3_write.py.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
CARDS = os.environ.get("GUARD_WRITE_CARDS") or os.path.join(TOOLS, "bench", "cards")   # env: self-tests only
OPEN_CARD_S = 24 * 3600


def _rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return p


def open_card_pins(path):
    """['card <id> pins <rel> at <md5>, disk is now <md5>'] for open cards (no result file yet) whose inputs name
    `path` with an md5 that matches neither the raw nor the canonical (header-stripped) bytes."""
    import hashlib
    import scope_header
    out = []
    ap = os.path.normcase(os.path.abspath(path))
    try:
        names = os.listdir(CARDS)
    except OSError:
        return out
    raw = None
    import time
    for n in names:
        m = re.match(r"^task_(.+)\.json$", n)
        if not m or os.path.exists(os.path.join(CARDS, "result_%s.json" % m.group(1))):
            continue
        try:                       # OPEN = written in the last 24 h and no result yet (an abandoned old card is not open)
            if time.time() - os.path.getmtime(os.path.join(CARDS, n)) > OPEN_CARD_S:
                continue
        except OSError:
            continue
        try:
            with open(os.path.join(CARDS, n), encoding="utf-8") as f:
                card = json.load(f)
        except (OSError, ValueError):
            continue
        for it in card.get("inputs") or []:
            if not isinstance(it, dict) or not it.get("md5") or not it.get("path"):
                continue
            ip = it["path"] if os.path.isabs(it["path"]) else os.path.join(ROOT, it["path"])
            if os.path.normcase(os.path.abspath(ip)) != ap:
                continue
            # gate-fp fp-43/45/47/48/49/50 (card 146-a1-1): a file the PINNING card itself lists in flags.write is that
            # card's authorised edit target - its pin is the pre-edit baseline, not a stale copy. Exempt for THAT card
            # only; a pin by a card whose flags.write does not cover the file still reports.
            try:
                import protocol
                if protocol.path_in_globs(path, (card.get("flags") or {}).get("write") or []):
                    continue
            except Exception:              # noqa: BLE001 - unreadable globs: not exempt
                pass
            if raw is None:
                with open(path, "rb") as f:
                    b = f.read()
                raw = {hashlib.md5(b).hexdigest(), hashlib.md5(scope_header.canonical_bytes(b)).hexdigest()}
            if it["md5"] not in raw:
                out.append("open card %s pins %s at md5 %s; the file on disk is now %s - that card works on a stale "
                           "copy (143-P1's failure): tell its owner, or re-pin" % (
                               m.group(1), _rel(path), it["md5"][:8], sorted(raw)[0][:8]))
    return out


def check_script(path):
    import scope_header as S
    probs = []
    h, err = S.read(path)
    if err:
        probs.append("scope header invalid: " + err)
    elif h is None:
        if _rel(path) not in S.NO_TOUCH:
            probs.append("no scope header - every tools/ script carries one (card chat-E3):\n"
                         "      # ---\n      # labview: none        # none | read | build\n"
                         "      # hardware: none       # none | camera | motor\n      # ---")
    ce = S.compile_error(path)
    if ce:
        probs.append("does not compile - " + ce)
    if h:
        probs.extend("dishonest header: " + x for x in S.honesty(path, h))
    probs.extend(open_card_pins(path))
    return probs


def check_json(path):
    import protocol
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except ValueError as e:
        return ["not valid JSON: %s" % e]
    except OSError:
        return []
    probs = []
    if isinstance(d, dict) and d.get("schema"):
        try:
            protocol.load_schema(d.get("schema"))
            known = True
        except (ValueError, OSError):
            known = False
        if known:
            ok, why = protocol.validate_obj(d)
            if not ok:
                probs.append("schema %s: %s" % (d.get("schema"), why))
            if d.get("schema") == "task/1":
                probs.extend("task/1 input pin stale: " + x for x in protocol.input_md5_changes(d))
    probs.extend(open_card_pins(path))
    return probs


def check_review(path):
    import guard_cycle as GC
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        return []
    if GC.DISPOSITION_MARK not in body:
        return []
    disp = body.split(GC.DISPOSITION_MARK, 1)[1]
    issued = set(GC.PRIOR_ART_RE.findall(body)) & set(GC.PRIOR_ART_SLUGS)
    probs = []
    for m in re.finditer(r"^(FIXED|REFUTED):[ \t]*([\w-]+)", disp, re.M):
        if m.group(2) not in issued:
            probs.append("%s line names slug %r, which is not one of this review's verdict slugs %s - the launch gate "
                         "will not release it (143-1); write it with `py tools/protocol.py release ...`" % (
                             m.group(1), m.group(2), sorted(issued) or "(none)"))
    try:
        _ok, bad = GC.released_slugs(path, body)
        probs.extend("FIXED %s rejected: %s" % (s, w) for s, w in bad)
    except Exception:                  # noqa: BLE001
        pass
    return probs


def decide(path):
    """[problems] for one written file (empty = clean)."""
    if not path:
        return []
    ap = os.path.abspath(path)
    low = ap.lower()
    inside_tools = os.path.normcase(ap).startswith(os.path.normcase(TOOLS) + os.sep)
    if inside_tools and low.endswith((".py", ".ps1")):
        return check_script(ap)
    if low.endswith(".json") and os.path.normcase(ap).startswith(os.path.normcase(ROOT) + os.sep):
        return check_json(ap)
    if low.endswith(".md") and re.search(r"[\\/]archive[\\/]peer[\\/][^\\/]*priorart[^\\/]*\.md$", ap, re.I):
        return check_review(ap)
    return []


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:                  # noqa: BLE001
        return 0
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    try:
        probs = decide(path)
    except Exception:                  # noqa: BLE001 - a broken checker never wedges writing
        return 0
    if not probs:
        return 0
    sys.stderr.write("WRITE-CHECK (tools/hooks/guard_write.py, card chat-E3) %s:\n" % _rel(path) +
                     "".join("  - %s\n" % p for p in probs) +
                     "Fix it now - it is seconds here and a failed card later (cycles 142-143: ~44 min).\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
