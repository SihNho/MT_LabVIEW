"""c60c_astcheck - static gate on tools/bench/diag_s3b_l0_localname_v2.py BEFORE it is launched.

The predecessor's gate (tools/bench/c60b_astcheck.py) with its checks KEPT, re-aimed at this cycle's
diagnostic, plus one addition (9): the forbidden alternative routes are named and machine-checked absent.
Touches NO LabVIEW, opens no COM, reads files only.

PREDICTION CONTRACT
  1 the file parses (ast.parse) and reports its line count and gate-site count
  2 `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` are NEITHER imported NOR called
  3 `allow_broken` is passed at MOST ONE site and only on a `.save(...)` call (AMENDED 2026-09-21 per
    Pre-decided 88; the blanket ban this line used to describe enforced the WITHDRAWN Pre-decided 81).
    WIDENED 2026-09-22 per Pre-decided 98(5): a site is ANY `allow_broken` argument that is not literal
    `False`, including `allow_broken=1` / `=flag` and the `**{"allow_broken": ...}` dict-splat form -
    the first coding matched only `ast.Constant True` and let all three past unseen. The gate NAME that
    is actually printed lives at :107 and is the authority; this line is its description.
  4 every `g.<verb>(...)` call names a `def <verb>` that already exists in tools/gscript.py
  5 every name imported from build_d1_v0 / diag_s2_scaffold / hash_probe / bench_prep exists there
  6 nothing under tools/recipes/ is opened for writing and nothing there is removed
  7 ROUTE CONFORMANCE for `move_in`, selected by `--route` (REPAIRED 2026-09-21, cycle 66)
      --route owner  (DEFAULT) : `move_in` is NEITHER imported NOR called
      --route movein           : `move_in` IS called at least once
    WHY. This gate was written for cycle 60's `owner` route, which deliberately excludes `move_in`. It was
    then reused as the fleet's generic static gate, so it FAILED BY CONSTRUCTION on every legitimate
    `move_in` build (cycle 64 `tools/bench/c64e_astcheck.log` 11/12, cycle 65 `tools/bench/c65_astcheck.log`
    11/12). That false positive is the SINGLETON intersection of runner cycles 49 n 50's failing gate lines
    (`tools/bench/cycle_runner.log:97,:100`) - i.e. a gate defect was the thing about to fire the runner's
    repeated-failure firefighter. The DEFAULT is `owner` so every existing invocation, which passes only a
    positional target, keeps this gate's pre-repair verdict byte for byte.
    NOT A COUNT, in either direction: stage M3a-1 mandates SEVEN `move_in` calls (the move set of
    tools/recipes/build_d1_m3a1.py:297-307 - this line said FIVE until 2026-09-22), so "called at most once" would
    be a second defect of the same shape. The printed gate NAME carries the route, so the two routes emit
    DIFFERENT failing lines and the runner's "same first failing gate line" matcher cannot conflate them.
  8 no owner comparison tests the literal 'Diagram' without also accepting 'TopLevelDiagram'
  9 the routes the brief FORBIDS are absent as calls: `build_invoke` (the peer's Invoke-seeded variant) and
    `copy_by_index` / `copy_into` / `move_by_label` (a donor switch)
 10 `%`-FORMAT ARITY (ADDED 2026-09-22, Pre-decided 100 §4, the accepted half). Every `"..." % (...)` site
    whose format string is a literal has its conversion-spec count compared with its argument count, and a
    MISMATCH FAILS. This is a REPAIR of a checker we already own, not a new device (the same reading used
    for `ensure_loaded` (Pre-decided 60) and for gate 3's widening under 98(5)).
    WHY. `tools/recipes/build_d1_m3a2.py:317` carried FIVE specs and FOUR arguments, raised `TypeError:
    not enough arguments for format string` in phase 1 of a 45-minute LabVIEW build, and cost the whole
    run - 1,062 hand-written lines launched at LabVIEW without one cheap static read. Counted the way
    CPython counts: `%%` consumes no argument, a `*` width or precision consumes one extra.
    NEVER SILENTLY PASSED: a site this gate cannot resolve statically (a non-literal format string that
    looks like a template, a non-tuple right operand where more than one spec is wanted, a `*`-splat in
    the argument tuple, a mapping `%(name)s` form) is PRINTED with its `file:line` under UNRESOLVED and
    counted in the gate's detail. Only a DEFINITE mismatch fails, because failing what cannot be read
    would be the same defect as gate 7's old `move_in` count.
    THE PASS COUNT IS SPLIT, and this is not cosmetic (`archive/peer/2026-09-22-c74-gate10-arity.md`,
    ANSWERED, opus max, findings 1 and 3, both ACCEPTED): VERIFIED = a literal tuple that was actually
    compared; ASSUMED = one spec against a non-tuple operand, which is an assumption, not a check. The
    first version added the two together and printed "145 checked OK".
    VALIDITY, ADDED 2026-09-22 (cycle-74 MATERIAL dispatch 5, the `c74-gate10-arity` review's SECOND
    finding, ACCEPTED with the scope limit the judgement session set). Arity alone let `"%d%"` and
    `"50% (of rows): %s"` through while CPython raises `ValueError`, and hand-appended prose inside a
    format string is exactly what cost this cycle a 71-second LabVIEW run. So:
      * every `%` in the literal that NO matched conversion span covers is REPORTED, and
      * a finding FAILS ONLY FOR A `str` LITERAL. A `bytes` literal is REPORTED AND NEVER FAILED,
        because PEP 461 makes `b"%b"` legal while `b` is not in `SPEC_RE`'s conversion class - failing
        it would be a false positive of exactly the shape this file warns about at :24.
    `%%` is covered by its own match and is therefore never stray.
"""
import argparse
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _parse_args(argv=None):
    """Added 2026-09-21 (cycle 66) for gate 7's route. The positional keeps the old `sys.argv[1]` contract
    and `--route` DEFAULTS TO `owner`, so an invocation that passes no flag behaves exactly as before."""
    ap = argparse.ArgumentParser(
        description="static gate on a tools/bench diagnostic, run BEFORE the diagnostic is launched")
    ap.add_argument("target", nargs="?", default="diag_s3b_l0_localname_v2.py",
                    help="script under tools/bench/ (an ABSOLUTE path is honoured as given)")
    ap.add_argument("--route", choices=("owner", "movein"), default="owner",
                    help="which construction route the target claims; decides gate 7's DIRECTION")
    return ap.parse_args(argv)


ARGS = _parse_args()
# os.path.join drops the prefix when the later part is absolute, so an absolute target passes through intact.
TARGET = os.path.join(ROOT, "tools", "bench", ARGS.target)
ROUTE = ARGS.route
GSCRIPT = os.path.join(ROOT, "tools", "gscript.py")
BANNED = ("remove_bad_wires_scripted", "remove_bad_wires", "gui_save")
FORBIDDEN_ROUTES = ("build_invoke", "copy_by_index", "copy_into", "move_by_label")
IMPORTS = {"build_d1_v0": os.path.join(ROOT, "tools", "recipes", "build_d1_v0.py"),
           "diag_s2_scaffold": os.path.join(ROOT, "tools", "bench", "diag_s2_scaffold.py"),
           "hash_probe": os.path.join(ROOT, "tools", "hash_probe.py"),
           "bench_prep": os.path.join(ROOT, "tools", "bench", "bench_prep.py")}
fails = []


def gate(name, ok, detail=""):
    if not ok:
        fails.append(name)
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""), flush=True)
    return ok


def defs_in(path):
    with open(path, encoding="utf-8") as f:
        return set(re.findall(r"^\s*def\s+(\w+)", f.read(), re.M))


def _is_literal_false(v):
    """Only a LITERAL False disarms the flag. `0`, `''`, `None` and every name are treated as ARMED,
    because this gate's job is to find sites that MIGHT pass a true value, not to evaluate Python."""
    return isinstance(v, ast.Constant) and v.value is False


def allow_broken_sites(tree):
    """Every call that passes `allow_broken` as anything other than literal `False`.

    REPAIRED 2026-09-22 (Pre-decided 98(5), finding 5 of archive/peer/2026-09-21-c71-astgate.md, the one
    load-bearing defect of the three). As first written the comprehension was

        ... for k in n.keywords if k.arg == "allow_broken"
            and isinstance(k.value, ast.Constant) and k.value.value is True

    so it saw ONLY the exact literal `allow_broken=True`. `allow_broken=1`, `allow_broken=flag` and
    `f(**{"allow_broken": True})` are all the same call to `gscript.save` at run time - `if allow_broken:`
    is truthiness - and all three passed this gate UNSEEN, i.e. a second broken-save site could have been
    added to a recipe without the gate noticing. Both forms are now matched, and the returned tuple carries
    a readable dump of the argument so the printed detail names WHAT was passed, not just how many.
    """
    sites = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        for k in n.keywords:
            if k.arg == "allow_broken":
                if not _is_literal_false(k.value):
                    sites.append((n, "allow_broken=" + ast.dump(k.value)[:70]))
            elif k.arg is None and isinstance(k.value, ast.Dict):
                for dk, dv in zip(k.value.keys, k.value.values):
                    if (isinstance(dk, ast.Constant) and dk.value == "allow_broken"
                            and not _is_literal_false(dv)):
                        sites.append((n, '**{"allow_broken": %s}' % ast.dump(dv)[:60]))
    return sites


# ---------------------------------------------------------------- gate 10: `%`-format arity
# The conversion-spec grammar CPython itself implements for `str.__mod__`. `%%` is matched by the same
# regex (conv == "%") and consumes no argument; a `*` width or precision consumes one extra argument.
SPEC_RE = re.compile(r"%(?:\((?P<key>[^)]*)\))?(?P<flags>[-+ #0]*)(?P<width>\*|\d+)?"
                     r"(?:\.(?P<prec>\*|\d+))?(?P<len>[hlL])?(?P<conv>[diouxXeEfFgGcrsa%])")


def _spec_spans(fmt):
    """Every non-overlapping `SPEC_RE` match, left to right - the spans the VALIDITY half calls COVERED."""
    spans, pos = [], 0
    while True:
        m = SPEC_RE.search(fmt, pos)
        if not m:
            break
        spans.append(m)
        pos = m.end()
    return spans


def _spec_count(fmt):
    """(arguments consumed, mapping keys named, positions of STRAY `%`).

    The third value is the VALIDITY half added 2026-09-22: a `%` that no matched conversion span covers.
    CPython raises `ValueError: unsupported format character` (or `incomplete format`) on such a literal
    whatever the arguments are, so it is a DEFINITE defect, not an arity guess. `%%` is covered by its
    own match and is never stray; the `%` of a mapping spec `%(k)s` is covered too.
    """
    n, keys, spans = 0, [], _spec_spans(fmt)
    for m in spans:
        if m.group("conv") == "%":
            continue
        if m.group("key") is not None:
            keys.append(m.group("key"))
            continue
        n += 1 + (m.group("width") == "*") + (m.group("prec") == "*")
    covered = [(m.start(), m.end()) for m in spans]
    stray = [i for i, ch in enumerate(fmt) if ch == "%"
             and not any(a <= i < b for a, b in covered)]
    return n, keys, stray


def _looks_like_a_format(left, right):
    """A `%` whose LEFT is not a literal string: is it a format site or is it arithmetic?

    Narrow on purpose. A literal tuple on the right is never arithmetic, and an ALL-CAPS name is this
    fleet's template convention (`FF_PROMPT % ...`, `CHILD % (...)`, `REVIEW % (...)`). Everything else
    is left alone, because reporting `i % 2` would drown the real reports.
    """
    return (isinstance(right, ast.Tuple)
            or (isinstance(left, ast.Name) and left.id.isupper() and len(left.id) > 2))


def percent_format_sites(tree, path):
    """Every `<literal string> % <args>` site, classified.

    Returns (mismatches, unresolved, verified, assumed, invalid, bytes_reported).

    `invalid` and `bytes_reported` are the VALIDITY half (2026-09-22, finding 2 of the same review).
    `invalid` = a `str` literal carrying a `%` no conversion span covers; it FAILS, because CPython
    raises `ValueError` on it for every argument list. `bytes_reported` = the SAME findings, and any
    arity mismatch, on a `bytes` literal: PRINTED AND NEVER FAILED (PEP 461 makes `b"%b"` legal while
    `b` is outside `SPEC_RE`'s conversion class, so failing a bytes site would be a false positive).

    The last two of the first four are SEPARATE, per finding 1 of
    `archive/peer/2026-09-22-c74-gate10-arity.md` (ANSWERED, opus max). As first written this function
    returned ONE `n_ok` counter over two populations: sites whose literal tuple was actually compared,
    and `want == 1` sites with a NON-tuple right operand, which are an ASSUMPTION - `"%s" % x` raises
    `TypeError: not all arguments converted` for every tuple `x` of length != 1, and the gate cannot see
    x's type. Filing that guess as a verified pass while the SAME unknowability at `want >= 2` was filed
    UNRESOLVED was the asymmetry the review named: the branch that inflates confidence was the silent one.
    Nothing is failed that was not failed before - the two counts are simply no longer added together.
    """
    mismatches, unresolved, verified, assumed = [], [], 0, 0
    invalid, bytes_reported = [], []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)):
            continue
        where = "%s:%d" % (os.path.basename(path), n.lineno)
        left = n.left
        if not (isinstance(left, ast.Constant) and isinstance(left.value, (str, bytes))):
            # Finding 3 of the same review: this branch used to `continue` SILENTLY, so a template held in
            # a module-level constant was invisible while two documents claimed nothing is silently passed.
            if _looks_like_a_format(left, n.right):
                unresolved.append("%s  the format string is not a literal (%s) - its arity is not readable "
                                  "here" % (where, type(left).__name__))
            continue                      # `i % 2` and friends: arithmetic, not our business
        is_str = isinstance(left.value, str)
        fmt = left.value if is_str else left.value.decode("latin-1", "replace")
        want, keys, stray = _spec_count(fmt)
        head = fmt.strip().replace("\n", " ")[:58]
        right = n.right
        # VALIDITY, checked BEFORE the arity branches so a mapping/unresolved site is still screened.
        # `fail_to` sends every finding on a `bytes` literal to the report-only list (PEP 461).
        fail_to = mismatches if is_str else bytes_reported
        if stray:
            (invalid if is_str else bytes_reported).append(
                "%s  %r carries %d %% not covered by any conversion spec, at offset(s) %r - CPython "
                "raises ValueError on this literal whatever the arguments are%s"
                % (where, head, len(stray), stray[:6], "" if is_str else "  [bytes: REPORTED, NOT FAILED]"))
        if keys:
            unresolved.append("%s  MAPPING form %r wants keys %r - not statically counted"
                              % (where, head, keys))
            continue
        if isinstance(right, ast.Tuple):
            if any(isinstance(e, ast.Starred) for e in right.elts):
                unresolved.append("%s  %r wants %d, argument tuple carries a *splat" % (where, head, want))
                continue
            got = len(right.elts)
            if got != want:
                fail_to.append("%s  %r wants %d arg(s), the tuple supplies %d%s"
                               % (where, head, want, got,
                                  "" if is_str else "  [bytes: REPORTED, NOT FAILED]"))
            else:
                verified += 1             # a literal tuple, actually compared: the only VERIFIED class
        elif want == 1:
            # ASSUMED, not verified: correct for any non-tuple `x`, and `TypeError` for a tuple of any
            # other length. Counted apart so the printed row can never read as 145 checks again.
            assumed += 1
        elif want == 0:
            fail_to.append("%s  %r takes NO argument (only %%%% literals) yet one is supplied%s"
                           % (where, head, "" if is_str else "  [bytes: REPORTED, NOT FAILED]"))
        else:
            # A bare name/call on the right MAY be a tuple of the right length at run time. Unknowable
            # statically, so it is REPORTED, never failed.
            unresolved.append("%s  %r wants %d arg(s); the right operand is a %s, not a literal tuple"
                              % (where, head, want, type(right).__name__))
    return mismatches, unresolved, verified, assumed, invalid, bytes_reported


def main():
    src = open(TARGET, encoding="utf-8").read()
    tree = ast.parse(src)
    n_gates = sum(1 for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "gate")
    gate("1 the diagnostic parses", True, "%d lines, %d gate sites" % (len(src.splitlines()), n_gates))

    called, attrs = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                called.add(f.id)
            elif isinstance(f, ast.Attribute):
                called.add(f.attr)
                if isinstance(f.value, ast.Name) and f.value.id == "g":
                    attrs.add(f.attr)
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    bad = [b for b in BANNED if b in called or b in imported]
    gate("2 remove_bad_wires_scripted / remove_bad_wires / gui_save neither imported nor called",
         not bad, "%r" % (bad,))

    # 3 AMENDED 2026-09-21 (cycle 57 firefighter) per Pre-decided 88 (docs/cycle27-plan.md:3063-3073):
    #   the blanket ban enforced the WITHDRAWN 81; the authorised shape is EXACTLY ONE
    #   `g.save(..., allow_broken=True)` call site and nothing else may pass the flag.
    #   WIDENED 2026-09-22 per Pre-decided 98(5): see allow_broken_sites() for what was missed and why.
    ab = allow_broken_sites(tree)
    ab_ok = all(isinstance(n.func, ast.Attribute) and n.func.attr == "save" for n, _d in ab)
    gate("3 allow_broken at MOST ONE site, not literal False, and only on a .save(...) call "
         "(Pre-decided 88 + 98(5))", len(ab) <= 1 and ab_ok,
         "%d site(s) %r, all .save(): %r" % (len(ab), [d for _n, d in ab], ab_ok))
    # A `**kwargs` splat whose dict is not a literal can hide the flag from any static reader. It is
    # REPORTED, never gated: failing every recipe that forwards **kwargs would be a second defect of
    # the same shape as the `move_in` count this file already carries a warning about at :24.
    opaque = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
              for k in n.keywords if k.arg is None and not isinstance(k.value, ast.Dict)]
    print("  NOTE  %d non-literal **splat call site(s); `allow_broken` inside one is not statically "
          "visible (reported, not gated)" % len(opaque), flush=True)

    gdefs = defs_in(GSCRIPT)
    missing = sorted(a for a in attrs if a not in gdefs and not a.startswith("_") and a not in ("CLAUDEDEV",))
    private = sorted(a for a in attrs if a.startswith("_"))
    gate("4 every g.<verb> called already exists as a def in tools/gscript.py", not missing,
         "verbs used: %r ; private helpers used: %r ; MISSING: %r"
         % (sorted(a for a in attrs if not a.startswith("_")), private, missing))
    gate("4b the private gscript helpers used also exist", all(p in gdefs for p in private),
         "%r" % [p for p in private if p not in gdefs])

    want = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module in IMPORTS:
            want.setdefault(n.module, set()).update(a.name for a in n.names)
    for mod, names in sorted(want.items()):
        d = defs_in(IMPORTS[mod])
        miss = sorted(x for x in names if x not in d)
        gate("5 %s exports %s" % (mod, ", ".join(sorted(names))), not miss, "MISSING %r" % (miss,))

    recipes_writes = [ln for ln in src.splitlines()
                      if "recipes" in ln and ("open(" in ln or "shutil" in ln or "remove(" in ln)]
    gate("6 nothing under tools/recipes/ is opened for writing or removed", not recipes_writes,
         "%r" % (recipes_writes[:3],))

    mi_called, mi_imported = "move_in" in called, "move_in" in imported
    mi_detail = "route=%s called=%r imported=%r" % (ROUTE, mi_called, mi_imported)
    if ROUTE == "owner":
        gate("7[owner] move_in is neither imported nor called",
             not mi_called and not mi_imported, mi_detail)
    else:
        gate("7[movein] move_in is called at least once", mi_called, mi_detail)

    lone = [ln.strip() for ln in src.splitlines()
            if re.search(r"==\s*[\"']Diagram[\"']", ln) and "TopLevelDiagram" not in ln]
    gate("8 no owner comparison tests the literal 'Diagram' alone", not lone, "%r" % (lone[:3],))

    forb = [r for r in FORBIDDEN_ROUTES if r in called or r in imported]
    gate("9 the forbidden routes (Invoke-seeded variant, donor switch) are absent as calls", not forb,
         "%r" % (forb,))

    mism, unres, verified, assumed, invalid, byt = percent_format_sites(tree, TARGET)
    for u in unres:
        print("  NOTE  10 UNRESOLVED %s" % u, flush=True)
    for m in mism:
        print("  NOTE  10 MISMATCH   %s" % m, flush=True)
    for v in invalid:
        print("  NOTE  10 INVALID    %s" % v, flush=True)
    for b in byt:
        print("  NOTE  10 BYTES      %s" % b, flush=True)
    gate("10 every literal `%`-format site is ARITY-correct and VALID "
         "(Pre-decided 100 SS4 + the c74-gate10-arity review, finding 2)", not mism and not invalid,
         "%d VERIFIED (literal tuple, compared), %d ASSUMED (one spec, non-tuple operand - NOT a check), "
         "%d MISMATCH %r, %d INVALID (a stray %% in a str literal) %r, %d bytes site(s) reported and NOT "
         "failed, %d unresolved (all printed above, never silently passed)"
         % (verified, assumed, len(mism), mism[:4], len(invalid), invalid[:4], len(byt), len(unres)))

    print("\n=== ASTCHECK %s%s" % ("OK" if not fails else "FAILED",
                                   ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
