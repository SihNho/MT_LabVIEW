r"""static_audit_recipe.py - the OFFLINE, no-LabVIEW audit of a staged-build recipe before it is launched.

WHY IT EXISTS. Cycle 46 act 6 could not run its static audit at all: every shell command naming
`tools/recipes/stage_d1_s1.py` was refused by the launch gate, so `ast.parse`, the hashes and the standing
constraint greps were never measured. The checks themselves were being retyped as ad-hoc one-liners each cycle.

WHAT ALREADY EXISTED (checked before writing this, CLAUDE.md "check what already exists"):
  * `ls tools/*.py` + `ls tools/bench | grep -iE "static|audit|precheck|lint"` -> `tools/doc_lint.py` lints .md
    documents, `tools/audit_cycle.py` audits a CYCLE's logs and reviews, `tools/op_selftest.py` runs op VIs.
    NOTHING audits a recipe .py file offline. No code is duplicated here.
  * The hashes are `stop_record.sha256_of` + hashlib; the standing constraints are the ones the cycle-46 brief
    and `docs/cycle27-plan.md` Pre-decided 29 name.

PREDICTION CONTRACT (each line is a gate; a FAIL is a refusal to launch, not a warning):
  S1  the file parses (`ast.parse`)
  S2  the file compiles (`py_compile`, to a temp .pyc that is discarded)
  S3  `allow_broken` appears in NO executable position (Pre-decided 29: banned in a stage artefact save).
      Measured from the AST: a comment or docstring SAYING it is banned is not a use of it.
  S4  `net_map` likewise (Pre-decided 17)
  S5  every `.save(` call is PLAIN - one positional path, no second positional, no keyword (so the defaults,
      `allow_broken=False` among them, are the ones in force)
  S6  `remove_bad_wires_scripted` appears EXACTLY ONCE as a call, and that call is NOT inside any for/while loop
      (measured from the AST, not from indentation)

CONTRACT HISTORY - WRITTEN DOWN BECAUSE THE CONTRACT WAS EDITED AFTER A RUN, WHICH IT SHOULD NOT HAVE BEEN.
`archive/peer/2026-09-19-staticaudit-falsepos.md` §1 (claude/hypothesis/opus-max, ANSWERED, $2.6391) found that the
version of this file which produced `tools/bench/static_audit_s1.log` (2026-09-19 22:54, 3 pass / 3 fail) NO LONGER
EXISTS: S3/S4/S5 were re-specified in place afterwards, so the log and the file disagree and the record cannot by
itself distinguish "mis-specified from the start" from "re-specified until it passed". There is no VCS here. The
only surviving trace of v1 is the gate strings in that log, so they are preserved verbatim:

    v1 (ran 22:54:59)  S3 "no `allow_broken` anywhere"      -> FAIL, lines [37, 124, 452, 472, 678]   (raw TEXT scan)
                       S4 "no `net_map` anywhere"           -> FAIL, lines [126, 656]                 (raw TEXT scan)
                       S5 "every `.save(` call is plain (no args)" -> FAIL, argful at [472, 678]
                       S1, S2, S6 PASS
    v2 (below)         S3/S4 measured from the AST; S5 = at most one positional and no keywords.

v2 is NOT claimed to be the stricter gate. The same review, §5, names three bypasses it still has (a bare-name
`save(TARGET, True)` as at `tools/gscript.py:1443`; a `Starred` unpack `g.save(*argv)`; one-file scope, when the
hazard `net_map` names is reaper firings in the import closure) and, in §1b, shows S6 to be UNSOUND for this very
recipe: `stage_d1_s1.py:788-789` dispatches phases from inside a `for` through a dict of function objects, so the
single `remove_bad_wires_scripted` at `:654` (inside `phase_c`) is lexically outside a loop and dynamically inside
one. Its runtime count is bounded only by `sel` being duplicate-free at `:775`, which S6 never measured.
Strengthening these gates is a DESIGN decision (the review argues the real gate belongs at the callee,
`docs/cycle27-plan.md:597`), deliberately left to a judgement session rather than taken here.

    py tools/bgrun.py --material --max-min 5 --log tools/bench/<name>.log \
        -- py -u tools/bench/static_audit_recipe.py <recipe path>
"""
import ast
import hashlib
import os
import py_compile
import sys
import tempfile

RESULTS = []


def gate(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("  PASS  " if ok else "  -> FAIL  ") + name + (("   " + detail) if detail else ""), flush=True)
    return bool(ok)


def loop_calls(tree, func_name):
    """Every Call to `func_name` (by bare name or attribute), with a flag: is it inside a for/while?"""
    out = []

    def walk(node, in_loop):
        for child in ast.iter_child_nodes(node):
            deeper = in_loop or isinstance(node, (ast.For, ast.While, ast.AsyncFor))
            if isinstance(child, ast.Call):
                f = child.func
                nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
                if nm == func_name:
                    out.append((getattr(child, "lineno", 0), deeper))
            walk(child, deeper)

    walk(tree, False)
    return out


def main(argv):
    if len(argv) != 1:
        print("usage: static_audit_recipe.py <recipe path>")
        return 2
    path = argv[0]
    ap = path if os.path.isabs(path) else os.path.abspath(path)
    with open(ap, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    print("=== static audit: %s ===" % path, flush=True)
    print("  md5    %s" % hashlib.md5(raw).hexdigest(), flush=True)
    print("  sha256 %s" % hashlib.sha256(raw).hexdigest(), flush=True)
    print("  bytes  %d" % len(raw), flush=True)
    print("  lines  %d" % len(text.splitlines()), flush=True)

    tree = None
    try:
        tree = ast.parse(text, ap)
        gate("S1 ast.parse", True)
    except SyntaxError as e:
        gate("S1 ast.parse", False, "%s line %s" % (e.msg, e.lineno))
    if tree is not None:
        d = tempfile.mkdtemp(prefix="sarec_")
        try:
            py_compile.compile(ap, cfile=os.path.join(d, "x.pyc"), doraise=True)
            gate("S2 py_compile", True)
        except py_compile.PyCompileError as e:
            gate("S2 py_compile", False, str(e)[:160])
        finally:
            try:
                os.remove(os.path.join(d, "x.pyc"))
            except OSError:
                pass
            try:
                os.rmdir(d)
            except OSError:
                pass

    # S3/S4 ARE MEASURED FROM THE AST, NOT FROM THE TEXT. A plain substring scan flagged five comment lines that
    # say `allow_broken=True` appears NOWHERE and two that say `net_map` is banned - i.e. the file's own statement
    # of the constraint counted as a violation of it. Only identifiers in executable positions count.
    if tree is not None:
        for tag, ident in (("S3", "allow_broken"), ("S4", "net_map")):
            hits = []
            for node in ast.walk(tree):
                if isinstance(node, ast.keyword) and node.arg == ident:
                    hits.append(getattr(node.value, "lineno", 0))
                elif isinstance(node, ast.Name) and node.id == ident:
                    hits.append(node.lineno)
                elif isinstance(node, ast.Attribute) and node.attr == ident:
                    hits.append(node.lineno)
                elif isinstance(node, ast.alias) and (node.name == ident or node.asname == ident):
                    hits.append(getattr(node, "lineno", 0))
            gate("%s `%s` in NO executable position" % (tag, ident), not hits,
                 "lines %s" % sorted(set(hits))[:8] if hits else "0 in code (comments/docstrings ignored)")

        # S5: PLAIN means the DEFAULTS are used - one positional path and nothing else. `g.save(TARGET)` is plain;
        # `g.save(TARGET, allow_broken=True)` is not.
        bad = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "save" and (len(node.args) > 1 or node.keywords)):
                bad.append(node.lineno)
        saves = [n.lineno for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "save"]
        gate("S5 every `.save(` call is plain (path only, all defaults)", not bad,
             "argful at lines %s" % bad if bad else "%d save call(s) at %s" % (len(saves), sorted(set(saves))))

        rbw = loop_calls(tree, "remove_bad_wires_scripted")
        gate("S6 exactly ONE remove_bad_wires_scripted call, outside any loop",
             len(rbw) == 1 and not rbw[0][1],
             "calls at %s (in_loop flags %s)" % ([l for l, _ in rbw], [b for _, b in rbw]))

    npass = sum(1 for _, ok in RESULTS if ok)
    nfail = len(RESULTS) - npass
    print("=== static audit: %d pass, %d fail ===" % (npass, nfail), flush=True)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
