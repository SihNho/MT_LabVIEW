# ---
# labview: none
# hardware: none
# ---
"""gen_capabilities.py - the scripting-function table of docs/toolkit-capabilities.md GENERATED FROM CODE, plus the
code-vs-doc DRIFT report doc_lint prints every cycle (card chat-F2 part 3, user 2026-10-06 "1~3번 모두 적용하도록 하자").

One row per function: name, arguments (from the def's AST), outcome contract / postconditions (tools/fncontract.py
TABLE), record status (tools/fn_records.py: fresh-pass / fresh-fail / stale / planned / none), source file:line.
Rows: every fncontract.TABLE row (all LabVIEW-touching public gscript functions + every Stage._op verb) and the recipe
functions of the stagekit/stagexec paths (fn_records.RECIPE_FUNCS).

The block sits between two HTML-comment markers APPENDED AT THE END of the doc, so every existing file:line citation into
the human-written prose above it stays valid (the same choice card chat-E3 made for script headers). Human prose outside
the block is never touched; the output is deterministic (no timestamp), so regenerating an unchanged tree is a no-op.

docs/NAMES.md is NOT generated: its terminal names are MEASURED from LabVIEW (node_terms reads), not derivable from code
or from the records (which hold none yet) - left alone, by the brief's own condition.

  py tools/gen_capabilities.py            # rewrite the block (append it the first time)
  py tools/gen_capabilities.py --check    # drift report only; exit 1 when the block differs from the code
"""
import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fncontract as FC                                                            # noqa: E402
import fn_records as FR                                                            # noqa: E402

DOC = os.path.join(ROOT, "docs", "toolkit-capabilities.md")
BEGIN = "<!-- GENERATED fn-table BEGIN (tools/gen_capabilities.py - do not edit by hand; regenerate) -->"
END = "<!-- GENERATED fn-table END -->"
ROW_RE = re.compile(r"^\| `([^`]+)` \|(.*)\|$")


def _args(node):
    """'target, cls, index, verify=True' from a FunctionDef (self dropped)."""
    a = node.args
    names = [x.arg for x in a.posonlyargs + a.args]
    defs = [None] * (len(names) - len(a.defaults)) + list(a.defaults)
    out = []
    for n, d in zip(names, defs):
        if n == "self":
            continue
        out.append(n if d is None else "%s=%s" % (n, ast.unparse(d)))
    if a.vararg:
        out.append("*" + a.vararg.arg)
    for k, d in zip(a.kwonlyargs, a.kw_defaults):
        out.append(k.arg if d is None else "%s=%s" % (k.arg, ast.unparse(d)))
    if a.kwarg:
        out.append("**" + a.kwarg.arg)
    return ", ".join(out)


def _cell(s, n=220):
    s = str(s).replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[:n - 3] + "..."


def rows(reg_dir=None):
    """[(name, args, contract, record, source)] sorted by name."""
    names = sorted(set(FC.TABLE) | set(FR.RECIPE_FUNCS))
    out = []
    for fn in names:
        p, defs, line = FR.locate(fn)
        if p is None:
            out.append((fn, "-", FC.describe(fn), "-", "NOT FOUND in code"))
            continue
        if fn.startswith("stagekit.op:"):
            args = "(Stage._op verb)"
            src = defs[0].split(":")[0] + ":%d" % line
        else:
            node = dict(FR._parsed(p)[1])[defs[0]]
            args = _args(node)
            src = "%s:%d" % (FR.rel(p), line)
        contract = FC.describe(fn) if fn in FC.TABLE else "recipe function - outcome via the Stage._op verb that calls it"
        rec = FR.status(fn, reg_dir)[0]
        out.append((fn, args, contract, rec, src))
    return out


def render(reg_dir=None):
    rs = rows(reg_dir)
    counts = {}
    for r in rs:
        counts[r[3]] = counts.get(r[3], 0) + 1
    lines = [BEGIN, "", "## Scripting functions - generated from code (card chat-F2)", "",
             "Outcome of every call: `ok | no_output | failed | timed_out` (tools/fncontract.py). Contract column = the "
             "declared postconditions `[measure, on_fail]` or `none - <reason>`. Record = tools/bench/fn_records/ "
             "(fresh-pass only while the function's source md5 equals the record's). %d rows; records: %s." % (
                 len(rs), ", ".join("%s %d" % kv for kv in sorted(counts.items()))), "",
             "| function | arguments | outcome contract | record | source |", "|---|---|---|---|---|"]
    for fn, args, contract, rec, src in rs:
        lines.append("| `%s` | %s | %s | %s | %s |" % (fn, _cell(args, 120), _cell(contract), rec, src))
    lines += ["", END]
    return "\n".join(lines) + "\n"


def split(text):
    """(before, block, after) - block None when the markers are absent."""
    i = text.find(BEGIN)
    if i < 0:
        return text, None, ""
    j = text.find(END, i)
    if j < 0:
        return text, None, ""
    j += len(END)
    if text[j:j + 1] == "\n":
        j += 1
    return text[:i], text[i:j], text[j:]


def write(doc=DOC, reg_dir=None):
    with open(doc, encoding="utf-8", newline="") as f:
        text = f.read()
    before, block, after = split(text)
    new = render(reg_dir)
    if block is None:
        out = text + ("" if text.endswith("\n") else "\n") + "\n" + new
    else:
        out = before + new + after
    if out != text:
        with open(doc, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return out != text


def _parse_block(block):
    d = {}
    for ln in (block or "").splitlines():
        m = ROW_RE.match(ln)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            d[m.group(1)] = cells
    return d


def drift(doc=DOC, reg_dir=None):
    """{'block': bool, 'missing': [...], 'gone': [...], 'stale': [...], 'record_changed': [...], 'moved': [...],
    'contract_changed': [...]} - code/registry vs the doc's generated block."""
    with open(doc, encoding="utf-8") as f:
        text = f.read()
    _b, block, _a = split(text)
    want = _parse_block(render(reg_dir))
    have = _parse_block(block)
    stale = sorted(fn for fn, c in want.items() if c[2] == "stale")
    common = sorted(set(want) & set(have))
    return {"block": block is not None, "missing": sorted(set(want) - set(have)), "gone": sorted(set(have) - set(want)),
            "stale": stale, "record_changed": [f for f in common if want[f][2] != have[f][2]],
            "moved": [f for f in common if want[f][3] != have[f][3]],
            "contract_changed": [f for f in common if want[f][:2] != have[f][:2]]}


def drift_line(d):
    if not d["block"]:
        return "the generated block is ABSENT - run py tools/gen_capabilities.py"
    parts = []
    for k in ("missing", "gone", "stale", "record_changed", "contract_changed", "moved"):
        if d[k]:
            parts.append("%s %d (%s%s)" % (k, len(d[k]), ", ".join(d[k][:5]), " ..." if len(d[k]) > 5 else ""))
    return "; ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--doc", default=DOC)
    a = ap.parse_args(argv)
    if a.check:
        d = drift(a.doc)
        line = drift_line(d)
        print("DRIFT: " + (line or "none"))
        print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if line else "PASS",
                                      "gates": {"pass": 0 if line else 1, "fail": 1 if line else 0},
                                      "first_fail": line[:200] or None, "artefacts": []}))
        return 1 if line else 0
    changed = write(a.doc)
    print("%s %s" % ("rewrote" if changed else "unchanged", FR.rel(a.doc)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
