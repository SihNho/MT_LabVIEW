r"""stop_record.py - the prior-art STOP RECORD and the LAUNCH GATE that reads it.

THE HOLE THIS CLOSES (docs/cycle18-plan.md, "What actually failed"). The prior-art device verifies that a review
HAPPENED and was disposed; nothing binds a recipe's LAUNCH to that review's VERDICT. On route-B run 3 the review
correctly said the recipe "was NOT executed" because it could not pass its own gate - and the recipe ran anyway
SIX SECONDS LATER, failed as predicted, and cost a further 781 s / $4.85 in the failed-prediction review that
followed. `guard_cycle.py` could not stop it: it gates a BUILD on the newest review's open verdicts, and by the
time run 3 launched that review had been annotated, so the file looked disposed.

THE DEVICE (plan Pre-decided 2, 3). A review whose verdict is anything other than `novel` writes a STOP RECORD
keyed to the recipe's PATH + FILE HASH. Any launch command naming that path is REFUSED while the record stands.

  * REFUSAL IS BY PATH, RELEASE IS QUALIFIED BY HASH. Matching a launch to a record must not depend on the
    recipe's bytes - otherwise re-saving the file would erase the record's reach, which is the bypass the plan
    names explicitly ("Re-saving the recipe changes the hash and does NOT clear the record - a changed hash means
    'unreviewed', not 'released'").
  * A release is stamped with the hash it released. The FIRST launch after a valid release line stamps the
    recipe's current hash into the record; later launches must present that same hash. Editing the recipe after
    the release therefore refuses again - the release covered bytes that no longer exist.
  * THE ONLY RELEASES ARE THE TWO THAT ALREADY EXIST (plan Pre-decided 3): `FIXED:` and `REFUTED:`, with the
    machine-checked conditions `guard_cycle.py` already enforces. No third form; `CYCLE_GUARD_OFF` is not one.

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md, "check what already exists"):
  * `ls tools/*.py` + `grep -rln "stop_record|stop record|launch gate" tools docs` -> nothing implements this.
  * The release-line validator DOES already exist, in `tools/hooks/guard_cycle.py`
    (`FIXED_RE`, `fixed_citations`, `fixed_slugs`, `review_time`, `stamp`, and the `REFUTED:` findall at its
    verdict gate). It is IMPORTED here, never reimplemented - two validators drift, and this file would be the
    third place the `FIXED:` conditions were spelled out. The import is LAZY (inside `_released`) because
    `guard_cycle` imports THIS module at its top level; a module-level import here would be circular.
    The `REFUTED:` half was an inline `re.findall` inside `guard_cycle.main()`; it is now
    `guard_cycle.released_slugs()`, which both callers use. That refactor is recorded in guard_cycle.py itself.

FAIL CLOSED, NARROWLY (plan/brief item d). If the store is missing-but-expected, unreadable or corrupt, any
command naming a path under `tools/recipes/` is REFUSED with the reason; every other command is untouched. An
internal error is treated the same way. A gate that cannot read its own record must not pretend everything is
released - and must not wedge `ls`.

API:
    write_stop_record(recipe_path, review_file, verdict, root=None) -> dict
    load_records() -> list[dict]                     (raises StoreError)
    check_command(command_string)   -> (allow: bool, message: str)

RECORD SHAPE (tools/bench/stop_records.json, a JSON list):
    {"recipe_path": "tools/recipes/x.py",            # project-relative, forward slashes, lower-cased
     "reviewed_sha256": "<hash of the recipe when the review saw it>",
     "review_file": "archive/peer/2026-09-18-priorart-x.md",
     "verdict": ["already-failed", "contradicted"],  # the open prior-art slugs; a string is also accepted
     "created_utc": "2026-09-18T01:02:03Z",
     "released": null | {"sha256": "<hash stamped at the first post-release launch>",
                         "line": "FIXED: ...", "when": "<utc>"}}
"""
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(HERE, "hooks")

STORE = os.path.join(HERE, "bench", "stop_records.json")
# THE "MISSING-BUT-EXPECTED" WITNESS. Without it, `rm tools/bench/stop_records.json` would be a silent release of
# every standing record, and a gate a delete can open is not a gate. The marker is written on the first successful
# store write and never removed, so: no marker + no store = a project that has never had a record (allow);
# marker + no store = the store was lost or deleted (refuse, narrowly).
MARKER = os.path.join(HERE, "bench", "stop_records.marker")

# What "narrowly" means when the store cannot be read: only commands that name a recipe are refused.
RECIPE_DIR_RE = re.compile(r"tools[\\/]recipes[\\/]", re.I)
# A filesystem path token: anything carrying a separator, plus drive-letter paths. Deliberately NOT keyed on
# `tools/recipes/` (brief item c) - the record index decides what is gated, not this regex.
# `=` is excluded from the relative alternative's PREFIX (repair 2026-09-24, docs/violation-decisions.md
# `## device-failed - 2026-09-24 03:53`): `--recipe=tools/recipes/x.py` used to yield the one token
# `--recipe=tools/recipes/x.py`, which matched no record, so the `=` spelling slipped past a refusal the
# space spelling got. Now both yield `tools/recipes/x.py`. Self-test: tools/bench/selftest_stoprecord_eqform.py.
PATH_TOKEN_RE = re.compile(r"""[A-Za-z]:[\\/][^\s'"|;&<>]+|[^\s'"|;&<>=]*[\\/][^\s'"|;&<>]+""")


# THE SECOND HALF OF THE CYCLE-44 DEADLOCK (cycle 46; `archive/peer/2026-09-19-stoprecord-release-deadlock-
# codex.md:32` and `…-opus.md:32`, both of which describe it; cycle 44 applied only the `_check` supersession
# half at :338-341). That remedy is "plant a LATER record for the same path" - but the planting command is
# `py tools/stop_record.py write --recipe <that path> …`, and `_check` matches ANY command carrying the path
# token (:301-302), so the record refused the one command that exists to supersede it.
# THE EXEMPTION, and nothing wider: a SHELL SEGMENT whose PROGRAM IN COMMAND POSITION is one of these two
# contributes no path tokens. Both can only ADD a record (or a review); neither can launch a build. Every other
# segment is scanned exactly as before, so `py -u tools/recipes/x.py`, `py tools/bgrun.py … -- py -u <recipe>`,
# a segment that merely MENTIONS stop_record.py, and even `py -u <recipe> && py tools/stop_record.py …` all stay
# refused. The check is per segment because every real command here arrives as `cd "<project>" && py …`.
EXEMPT_PROGRAMS = ("tools/stop_record.py", "tools/prior_art_review.py")
# Shell separators. Tokens never contain these characters (PATH_TOKEN_RE excludes them), so splitting here
# cannot cut a path in half.
SEGMENT_SPLIT_RE = re.compile(r"&&|\|\||[;|\n]")
# Command position inside one segment: optional env-var prefix, the interpreter, its flags, then the script.
COMMAND_POSITION_RE = re.compile(
    r"^\s*(?:\w+=[^\s]+\s+)*"
    r"[^\s'\"|;&]*\bpy(?:thon)?[\w.]*(?:\.exe)?\s+(?:-\w+\s+)*['\"]?([^\s'\"|;&]+\.py)",
    re.I)


def exempt_program(command_string):
    """The path of the command-position program of this SEGMENT when it is one of EXEMPT_PROGRAMS, else ''."""
    m = COMMAND_POSITION_RE.match(command_string or "")
    if not m:
        return ""
    prog = keys_for(m.group(1))
    for e in EXEMPT_PROGRAMS:
        if prog & keys_for(e):
            return e
    # THE BGRUN WRAPPER (repair 2026-09-24 cycle 71, docs/violation-decisions.md `## device-failed - 2026-09-24
    # 03:53` family): guard_bash requires every prior-art review to run under bgrun, and bgrun is the program in
    # command position, so the exemption above never saw `prior_art_review.py` and a recipe's review could not be
    # launched at all. When the program is bgrun.py, judge the command after bgrun's `--` instead. A recipe
    # launched under bgrun (`bgrun ... -- py -u <recipe>`) is still not exempt. Self-test:
    # tools/bench/selftest_stoprecord_bgrun.py.
    if prog & keys_for(BGRUN_PROGRAM):
        parts = BGRUN_SEP_RE.split(command_string[m.end():], maxsplit=1)
        if len(parts) == 2:
            return exempt_program(parts[1])
    return ""


BGRUN_PROGRAM = "tools/bgrun.py"
BGRUN_SEP_RE = re.compile(r"\s--(?:\s+|$)")


class StoreError(Exception):
    """The record store exists in principle but cannot be trusted right now."""


def _root():
    return ROOT


def keys_for(path):
    """The match keys for one path token or record path: ('rel', <project-relative, posix, lower>) and
    ('abs', <normcase absolute>). Two keys, so a launch written as `tools/recipes/x.py`, `tools\\recipes\\x.py`
    or an absolute path all meet the same record."""
    t = (path or "").strip().strip("'\"").rstrip(",;")
    if not t:
        return set()
    out = set()
    try:
        if os.path.isabs(t):
            ap = os.path.abspath(t)
            out.add(("abs", os.path.normcase(ap)))
            try:
                rel = os.path.relpath(ap, _root())
            except ValueError:                       # different drive on Windows
                rel = None
            if rel and not rel.startswith(".."):
                out.add(("rel", rel.replace(os.sep, "/").lower()))
        else:
            rel = os.path.normpath(t.replace("\\", "/")).replace(os.sep, "/")
            out.add(("rel", rel.lower()))
            out.add(("abs", os.path.normcase(os.path.abspath(os.path.join(_root(), rel)))))
    except (OSError, ValueError):
        return out
    return out


def sha256_of(path):
    try:
        with open(path, "rb") as f:
            h = hashlib.sha256()
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _abs(path):
    p = (path or "").strip().strip("'\"")
    if not p:
        return ""
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(_root(), p.replace("/", os.sep)))


def _rel(path):
    """Project-relative, forward slashes, lower-cased - the stored form. An absolute path outside the project is
    kept as-is (lower-cased), so a scratch record in a temp directory still matches itself."""
    p = (path or "").strip().strip("'\"")
    if not p:
        return ""
    if os.path.isabs(p):
        try:
            r = os.path.relpath(p, _root())
        except ValueError:
            return p.replace("\\", "/").lower()
        if not r.startswith(".."):
            return r.replace(os.sep, "/").lower()
        return os.path.abspath(p).replace("\\", "/").lower()
    return os.path.normpath(p.replace("\\", "/")).replace(os.sep, "/").lower()


def _utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_records():
    """Every standing record. Raises StoreError when the store cannot be trusted - callers fail closed."""
    if not os.path.exists(STORE):
        if os.path.exists(MARKER):
            raise StoreError("the stop-record store %s is MISSING, but %s records that it existed - a deleted "
                             "store is not a release" % (_rel(STORE), _rel(MARKER)))
        return []
    try:
        with open(STORE, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        raise StoreError("the stop-record store %s is unreadable: %s" % (_rel(STORE), e))
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise StoreError("the stop-record store %s is not valid JSON: %s" % (_rel(STORE), e))
    if not isinstance(data, list):
        raise StoreError("the stop-record store %s must be a JSON list, got %s"
                         % (_rel(STORE), type(data).__name__))
    for i, r in enumerate(data):
        if not isinstance(r, dict) or not r.get("recipe_path"):
            raise StoreError("record %d in %s has no `recipe_path`" % (i, _rel(STORE)))
        rel = r.get("released")
        if rel is not None and not isinstance(rel, dict):
            raise StoreError("record %d in %s has a `released` that is not an object" % (i, _rel(STORE)))
    return data


def save_records(records):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, STORE)
    if not os.path.exists(MARKER):
        try:
            with open(MARKER, "w", encoding="utf-8") as f:
                f.write("the stop-record store exists; its disappearance is a fault, not a release.\n")
        except OSError:
            pass


def verdict_slugs(record):
    v = record.get("verdict")
    if v is None:
        return []
    if isinstance(v, str):
        return [s.strip() for s in re.split(r"[,\s]+", v) if s.strip()]
    return [str(s).strip() for s in v if str(s).strip()]


def write_stop_record(recipe_path, review_file, verdict, root=None):
    """Plant a stop record for `recipe_path`, keyed to the bytes the review saw.

    `verdict` is the list of prior-art slugs that stopped the work (anything but `novel`). Re-planting the same
    (path, hash, review) updates that record instead of appending a duplicate; a DIFFERENT hash appends a new
    record, because a different recipe was reviewed."""
    if root and root != ROOT:
        # Explicit, non-sticky: resolve against the caller's root without mutating this module's.
        recipe_path = recipe_path if os.path.isabs(recipe_path) else os.path.join(root, recipe_path)
        review_file = review_file if os.path.isabs(review_file) else os.path.join(root, review_file)
    rp = _rel(recipe_path)
    sha = sha256_of(_abs(recipe_path))
    rf = _rel(review_file)
    slugs = verdict if isinstance(verdict, (list, tuple)) else [verdict]
    slugs = [str(s).strip() for s in slugs if str(s).strip() and str(s).strip() != "novel"]
    rec = {"recipe_path": rp, "reviewed_sha256": sha, "review_file": rf,
           "verdict": slugs, "created_utc": _utc(), "released": None}
    try:
        records = load_records()
    except StoreError:
        # A corrupt store must not silently lose the record being written. Writing is the only operation allowed
        # to start a fresh list, and it says so in the record itself.
        records = []
        rec["note"] = "written over an unreadable store"
    for i, r in enumerate(records):
        if (_rel(r.get("recipe_path")) == rp and r.get("reviewed_sha256") == sha
                and _rel(r.get("review_file")) == rf):
            rec["created_utc"] = r.get("created_utc", rec["created_utc"])
            rec["released"] = r.get("released")
            records[i] = rec
            save_records(records)
            return rec
    records.append(rec)
    save_records(records)
    return rec


def _released(record):
    """(released: bool, line: str, why: str) - is this record's review carrying a VALID release line?

    The validator is `guard_cycle.released_slugs`, imported (never copied). Import is lazy: guard_cycle imports
    this module at its top level, so a module-level import here would be circular."""
    rf = _abs(record.get("review_file"))
    if not rf or not os.path.isfile(rf):
        return False, "", ("the review file named by the record is not on disk: %s"
                           % (record.get("review_file") or "(none)"))
    try:
        with open(rf, "r", encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError as e:
        return False, "", "the review file %s is unreadable: %s" % (record.get("review_file"), e)
    if HOOKS not in sys.path:
        sys.path.insert(0, HOOKS)
    import guard_cycle                                     # noqa: E402 - lazy on purpose, see the docstring
    ok, bad = guard_cycle.released_slugs(rf, body)
    want = verdict_slugs(record)
    missing = [s for s in want if s not in ok] if want else ([] if ok else ["(any)"])
    if missing:
        why = ("no valid release line in %s for: %s" % (record.get("review_file"), ", ".join(missing)))
        if bad:
            why += "".join("\n      rejected FIXED : %s - %s" % (s, w) for s, w in bad)
        return False, "", why
    if want:
        pat = r"^(?:FIXED|REFUTED):[ \t]*%s\b.*$" % re.escape(want[0])
    else:
        pat = r"^(?:FIXED|REFUTED):.*$"
    m = re.search(pat, body, re.M)
    return True, (m.group(0).strip() if m else "(release line found)"), ""


def _refusal(record, head, detail):
    return ("BLOCKED by tools/stop_record.py (the prior-art LAUNCH GATE, docs/cycle18-plan.md Pre-decided 2): "
            "%s\n"
            "  recipe      : %s\n"
            "  review      : %s\n"
            "  verdict     : %s\n"
            "  reviewed sha: %s\n"
            "  %s\n\n"
            "A prior-art verdict other than `novel` stops the work, and cycle 18 exists because stopping the\n"
            "BUILD was not enough: on route-B run 3 the recipe LAUNCHED six seconds after the review that said it\n"
            "could not pass. The only releases are the two that already exist, written into the review file\n"
            "itself and paid for with a citation:\n"
            "  REFUTED: <slug> - <file>:<line> says X, which does not cover Y because ...\n"
            "  FIXED:   <slug> - <path>:<line> - <one sentence saying what changed>\n"
            "(`FIXED:` releases only if the cited path exists, changed AFTER the review, and the line sits under\n"
            "'## What was done with it'.) An assertion is not a refutation and a promise is not a fix.\n"
            "CYCLE_GUARD_OFF is not a release and does not reach this gate.\n"
            % (head, record.get("recipe_path"), record.get("review_file") or "(none)",
               ", ".join(verdict_slugs(record)) or "(unspecified)",
               (record.get("reviewed_sha256") or "(none)")[:12], detail))


def _check(command_string):
    records = load_records()
    if not records:
        return True, ""
    cmd = command_string or ""
    tokens = set()
    for seg in SEGMENT_SPLIT_RE.split(cmd):
        if exempt_program(seg):      # see EXEMPT_PROGRAMS above - the record must not refuse its own remedy
            continue
        for t in PATH_TOKEN_RE.findall(seg):
            tokens |= keys_for(t)
    if not tokens:
        return True, ""
    pending = []
    for i, record in enumerate(records):
        if not (keys_for(record.get("recipe_path")) & tokens):
            continue
        ok, line, why = _released(record)
        if not ok:
            return False, _refusal(record, "this recipe is STOPPED by a prior-art verdict that is neither "
                                           "refuted nor fixed.", why)
        cur = sha256_of(_abs(record.get("recipe_path")))
        if cur is None:
            return False, _refusal(record, "this recipe has a released stop record, but the file itself cannot "
                                           "be read, so the release cannot be matched to any bytes.",
                                   "unreadable: %s" % record.get("recipe_path"))
        rel = record.get("released")
        if rel is None:
            record["released"] = {"sha256": cur, "line": line, "when": _utc()}
            pending.append(record)
            continue
        if rel.get("sha256") == cur:
            continue
        # SUPERSESSION (cycle 44; `archive/peer/2026-09-19-stoprecord-release-deadlock-codex.md:91-107`,
        # ACCEPTED AND APPLIED). An ALREADY-RELEASED record whose stamped bytes no longer exist is SKIPPED when a
        # LATER record stands for the same normalised path - because that later record is the review of the bytes
        # on disk now, and it is the one entitled to decide. Without this, the first release poisoned the pathname
        # for good: `write_stop_record` deliberately APPENDS a record for a different hash (:203-:237) and this
        # gate's own refusal says "Get the edited recipe reviewed" - and then the old record short-circuited
        # before the new one was ever reached. Measured twice, cycles 42 and 43, each of which had to RENAME the
        # recipe (v2 -> v3) to relaunch a bug fix judgement had already released; the cycle-43 retrospective
        # scored it `device-failed`. NOTHING THE GATE EXISTS FOR IS NARROWED: an UNDISPOSED older record still
        # refuses above (`_released` is checked first, for every matching record), and the later record still
        # refuses until its OWN findings carry valid `FIXED:`/`REFUTED:` lines - it is evaluated on this same
        # pass, by the same rules, and stamps only its own bytes. Acceptance:
        # `tools/bench/selftest_stoprecord_supersession.py` (case 1 releases; cases 2 and 3 must still refuse).
        later_same_path = any(_rel(r.get("recipe_path")) == _rel(record.get("recipe_path"))
                              for r in records[i + 1:])
        if later_same_path:
            continue
        return False, _refusal(
            record,
            "this recipe was RELEASED for different bytes than the ones on disk now.",
            "released for sha %s, on disk now %s - a changed hash means UNREVIEWED, not released. Re-saving a\n"
            "  recipe does not clear its record (docs/cycle18-plan.md Pre-decided 2). Get the edited recipe "
            "reviewed,\n  or cite the edit with a fresh FIXED: line in a review that post-dates it."
            % ((rel.get("sha256") or "(none)")[:12], cur[:12]))
    if pending:
        try:
            save_records(records)
        except OSError as e:
            return False, ("BLOCKED by tools/stop_record.py: a release could not be stamped into %s (%s). "
                           "The gate refuses rather than allow an unrecorded release." % (_rel(STORE), e))
    return True, ""


def check_command(command_string):
    """(allow, message). The launch gate. Fails CLOSED for commands naming `tools/recipes/`, and never wedges
    anything else - a defect in this module must not stop `ls`."""
    try:
        return _check(command_string)
    except StoreError as e:
        if RECIPE_DIR_RE.search(command_string or ""):
            return False, ("BLOCKED by tools/stop_record.py (fail-closed): the prior-art stop-record store "
                           "cannot be read, so no launch of a recipe can be shown to be released.\n"
                           "  %s\n"
                           "Restore tools/bench/stop_records.json (it is a JSON list) or, if it was genuinely "
                           "lost, re-plant the standing records from the archived prior-art reviews. Commands "
                           "that do not name a recipe are unaffected.\n" % e)
        return True, ""
    except Exception as e:                           # noqa: BLE001 - a gate crash must not wedge the session
        if RECIPE_DIR_RE.search(command_string or ""):
            return False, ("BLOCKED by tools/stop_record.py (fail-closed): the launch gate itself failed while "
                           "checking this command: %r\n"
                           "Fix tools/stop_record.py before launching a recipe; other commands are "
                           "unaffected.\n" % (e,))
        return True, ""


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser(description="prior-art stop records and the launch gate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write", help="plant a stop record")
    w.add_argument("--recipe", required=True)
    w.add_argument("--review", required=True)
    w.add_argument("--verdict", nargs="+", required=True)
    c = sub.add_parser("check", help="ask the gate about a command line")
    c.add_argument("command", nargs="+")
    sub.add_parser("list", help="print the standing records")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        r = write_stop_record(a.recipe, a.review, a.verdict)
        print(json.dumps(r, indent=2))
        return 0
    if a.cmd == "check":
        allow, msg = check_command(" ".join(a.command))
        print("ALLOW" if allow else msg)
        return 0 if allow else 2
    try:
        for r in load_records():
            print("%-45s %s  %s" % (r.get("recipe_path"), (r.get("reviewed_sha256") or "")[:12],
                                    "RELEASED" if r.get("released") else "STOPPED"))
    except StoreError as e:
        print("store error: %s" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
