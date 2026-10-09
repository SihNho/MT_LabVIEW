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

Card chat-T7 (2026-10-09): a SECOND generated block, the fn-LIST - every public function of every SHARED tools file (import graph),
regenerated detached by tools/hooks/guard_write.py on a write to a shared file and at every cycle end by tools/cycle_runner.py.

  py tools/gen_capabilities.py            # rewrite both blocks (append them the first time)
  py tools/gen_capabilities.py --check    # drift report only; exit 1 when a block differs from the code
  py tools/gen_capabilities.py --summary  # rewrite + one CAPABILITIES-SUMMARY counts line (cycle_runner.capabilities_hook)
"""
import argparse
import ast
import json
import os
import re
import sys
import time

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
    """The fn-table block text (markers included) from fncontract.TABLE + fn_records. Returns a str. Self-test: selftest_fn_f2.py."""
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


def write(doc=DOC, reg_dir=None, with_list=True, root=None):
    """Rewrite the generated fn-table block (and, card chat-T7, the fn-list block after it - with_list) in `doc`; returns True when
    the file changed. Deterministic: an unchanged tree is a no-op. Self-tests: selftest_fn_f2.py, selftest_t7_capabilities.py."""
    with open(doc, encoding="utf-8", newline="") as f:
        text = f.read()
    before, block, after = split(text)
    new = render(reg_dir)
    if block is None:
        out = text + ("" if text.endswith("\n") else "\n") + "\n" + new
    else:
        out = before + new + after
    if with_list:
        out = put_list(out, render_list(root))
    if out != text:
        with open(doc, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return out != text


# ============================================================================================== THE FUNCTION LIST (card chat-T7)
# User 2026-10-09 ("전부 적용"; "8개만 보기에는 너무 적지 않은가"; "함수가 바뀌면 목록 갱신 되어야하는거 아님?"): the fn-table above covers only
# the LabVIEW-touching gscript functions + stage verbs + recipe functions. The LIST below names EVERY public function (no leading `_`,
# top level + public methods of public classes) of every SHARED file - a .py under tools/ (tools/, tools/bench/, tools/recipes/,
# tools/hooks/) that at least one OTHER file imports, measured from the IMPORT GRAPH in one regex pass (import / from ... import /
# importlib.import_module("x") / __import__("x") / K.mod("x")), never from a fixed list. Per function: name(args), the docstring's first
# line, the self-test the docstring names. A second block between its own markers, after the fn-table; the shared set is cached in
# tools/bench/capabilities_shared.json for tools/hooks/guard_write.py, which re-runs this file DETACHED when a shared file is written
# (`--hook-run`: one run at a time, a write during a run sets a re-run flag). tools/cycle_runner.py runs it at every cycle end.
LIST_BEGIN = "<!-- GENERATED fn-list BEGIN (tools/gen_capabilities.py - every public function of every SHARED tools file, by import graph; do not edit by hand) -->"
LIST_END = "<!-- GENERATED fn-list END -->"
SCAN_DIRS = (("tools", ""), ("tools/bench", "bench"), ("tools/recipes", "recipes"), ("tools/hooks", "hooks"))   # precedence order
SHARED_CACHE = os.path.join(HERE, "bench", "capabilities_shared.json")
IMPORT_RE = re.compile(r"^[ \t]*(?:from[ \t]+([A-Za-z_][\w.]*)[ \t]+import\b|import[ \t]+([A-Za-z_][\w. \t,]*))", re.M)
DYN_IMPORT_RE = re.compile(r"(?:import_module|__import__|\bmod)\(\s*[\"']([A-Za-z_][\w.]*)[\"']\s*\)")
SELFTEST_RE = re.compile(r"(selftest_\w+(?:\.py)?|tools/\w+\.py selftest|\w+\.py selftest)")
LOC_NOTE = {"tools/bench": "shared file in the bench folder (move to tools/ later)", "tools/hooks": "hook - reference",
            "tools/recipes": "recipe imported by another file", "tools": "shared module"}


def _modules(root):
    """{module name: rel path} over SCAN_DIRS, the first directory in precedence order winning a name."""
    out = {}
    for rel_dir, sub in SCAN_DIRS:
        d = os.path.join(root, "tools", sub) if sub else os.path.join(root, "tools")
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for n in names:
            if n.endswith(".py") and n[:-3] not in out:
                out[n[:-3]] = rel_dir + "/" + n
    return out


def imported_names(text):
    """Top-level module names a source text imports (static and importlib / __import__ / K.mod string forms)."""
    out = set()
    for m in IMPORT_RE.finditer(text):
        if m.group(1):
            out.add(m.group(1).split(".")[0])
        else:
            for part in m.group(2).split(","):
                w = part.strip().split()
                if w:
                    out.add(w[0].split(".")[0])
    out.update(x.split(".")[0] for x in DYN_IMPORT_RE.findall(text))
    return out


def shared_files(root=None):
    """{rel path of a SHARED file: sorted [rel paths of the OTHER files that import it]} - the import graph over every .py under
    tools/ (one regex pass per file). Self-test: tools/bench/selftest_t7_capabilities.py."""
    root = root or ROOT
    mods = _modules(root)
    users = {}
    for rel_dir, sub in SCAN_DIRS:
        d = os.path.join(root, "tools", sub) if sub else os.path.join(root, "tools")
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for n in names:
            if not n.endswith(".py"):
                continue
            me = rel_dir + "/" + n
            try:
                with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            for mname in imported_names(text):
                tgt = mods.get(mname)
                if tgt and tgt != me:
                    users.setdefault(tgt, set()).add(me)
    return dict((k, sorted(v)) for k, v in sorted(users.items()))


def _doc_first(node):
    d = ast.get_docstring(node) or ""
    return d.strip().split("\n")[0].strip() if d.strip() else ""


def _selftest_of(node):
    m = SELFTEST_RE.search(ast.get_docstring(node) or "")
    return m.group(1) if m else ""


def module_functions(path):
    """[(name, args, first docstring line, self-test named in the docstring, line)] of a file's public top-level functions and the
    public methods of its public classes (`Class.method`; a class row carries the class docstring). [] when it does not parse."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=path)
    except (OSError, SyntaxError, ValueError):
        return []
    out = []
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_"):
            out.append((n.name, _args(n), _doc_first(n), _selftest_of(n), n.lineno))
        elif isinstance(n, ast.ClassDef) and not n.name.startswith("_"):
            out.append((n.name, "(class)", _doc_first(n), _selftest_of(n), n.lineno))
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_"):
                    out.append(("%s.%s" % (n.name, m.name), _args(m), _doc_first(m), _selftest_of(m), m.lineno))
    return out


# ---- descriptions of EXISTING functions in a side file (card chat-T8, user 2026-10-09 "권장안대로 처리"): writing a docstring into an
# existing function would shift every file:line citation below it, so its one-line description lives in docs/fn_descriptions.json under
# '<module>.<function>' (module = file name without .py, function = name or Class.method). A docstring always wins over the side file.
FN_DESC_REL = "docs/fn_descriptions.json"
DESC_SCHEMA = "fn-descriptions/1"
UNDOC = "(undocumented)"


def _read_descs(root=None, path=None):
    """({key: description}, error or '') from the side file; ({}, '') when it is absent."""
    p = path or os.path.join(root or ROOT, *FN_DESC_REL.split("/"))
    if not os.path.exists(p):
        return {}, ""
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        return {}, "side file unreadable: %s" % str(e)[:120]
    if not isinstance(d, dict) or d.get("schema") != DESC_SCHEMA or not isinstance(d.get("items"), dict):
        return {}, "side file is not schema %s with an items map" % DESC_SCHEMA
    return dict((str(k), str(v).strip()) for k, v in d["items"].items() if str(v).strip()), ""


def load_descriptions(root=None, path=None):
    """{'<module>.<function>': one-line description} from docs/fn_descriptions.json ({} when absent or malformed - stale_descriptions
    reports a malformed file). Self-test: selftest_t7_capabilities.py."""
    return _read_descs(root, path)[0]


def describe_row(module, name, doc, descs):
    """(text, source) of one fn-list row: the docstring's first line -> 'docstring'; else the side file's '<module>.<name>' entry ->
    'side file'; else ('(undocumented)', '-'). Self-test: selftest_t7_capabilities.py."""
    if doc:
        return doc, "docstring"
    t = descs.get("%s.%s" % (module, name))
    return (t, "side file") if t else (UNDOC, "-")


def stale_descriptions(root=None, path=None):
    """Sorted side-file keys whose function no longer exists (no tools .py of that module name, or no public function / Class.method
    of that name in it), plus one '(side file unreadable ...)' entry for a malformed file. drift() carries them; doc_lint L12 prints
    them as a WARN. Self-test: selftest_t7_capabilities.py."""
    root = root or ROOT
    descs, err = _read_descs(root, path)
    out = ["(%s)" % err] if err else []
    mods, names = _modules(root), {}
    for k in sorted(descs):
        mod, _dot, fn = k.partition(".")
        p = mods.get(mod)
        if p is None or not fn:
            out.append(k)
            continue
        if mod not in names:
            names[mod] = set(x[0] for x in module_functions(os.path.join(root, p.replace("/", os.sep))))
        if fn not in names[mod]:
            out.append(k)
    return out


def described_rows(root=None, path=None):
    """[(rel path, location note, importers, [(name, args, text, source, self-test, line)])] - list_rows with each row's description
    resolved by describe_row (docstring, else side file, else undocumented). Self-test: selftest_t7_capabilities.py."""
    descs = load_descriptions(root, path)
    out = []
    for p, note, users, r in list_rows(root):
        mod = p.rsplit("/", 1)[-1][:-3]
        out.append((p, note, users, [(n, a) + describe_row(mod, n, d, descs) + (st, ln) for n, a, d, st, ln in r]))
    return out


def list_rows(root=None):
    """[(rel path, location note, importers, [module_functions rows])] for every shared file, tools/ first then bench / recipes /
    hooks, each group by name. Writes the shared-set cache (SHARED_CACHE) as a side effect when root is the project root."""
    root = root or ROOT
    sh = shared_files(root)
    order = dict((rd, i) for i, (rd, _s) in enumerate(SCAN_DIRS))
    keys = sorted(sh, key=lambda p: (order.get(p.rsplit("/", 1)[0], 9), p))
    out = [(p, LOC_NOTE.get(p.rsplit("/", 1)[0], ""), sh[p], module_functions(os.path.join(root, p.replace("/", os.sep)))) for p in keys]
    if os.path.normcase(os.path.abspath(root)) == os.path.normcase(os.path.abspath(ROOT)):
        write_shared_cache([p for p, _n, _u, _r in out])
    return out


def write_shared_cache(paths, cache=None):
    """Write {schema capabilities-shared/1, files: [...]} to the cache guard_write reads (only when its content changes)."""
    cache = cache or SHARED_CACHE
    new = json.dumps({"schema": "capabilities-shared/1", "files": sorted(paths)}, indent=0, sort_keys=True) + "\n"
    try:
        with open(cache, encoding="utf-8") as f:
            if f.read() == new:
                return False
    except OSError:
        pass
    with open(cache, "w", encoding="utf-8") as f:
        f.write(new)
    return True


def render_list(root=None):
    """The fn-list block text (markers included): a module table of contents, then one section per shared file."""
    rows = described_rows(root)
    nf = sum(len(r) for _p, _n, _u, r in rows)
    ns = sum(1 for _p, _n, _u, r in rows for x in r if x[3] == "side file")
    nd = sum(1 for _p, _n, _u, r in rows for x in r if x[3] == "-")
    lines = [LIST_BEGIN, "", "## Every public function of the shared tools files - generated from code (card chat-T7)", "",
             "A file is SHARED when at least one OTHER file under tools/ imports it (import graph, measured at generation; cache "
             "tools/bench/capabilities_shared.json). Look here before writing any logic (docs/script-writing.md rule 8). "
             "%d files, %d functions: %d described by a docstring, %d by %s (existing functions, card chat-T8), %d undocumented "
             "(per file in the table below). Regenerated at every cycle end and when a shared file is written." % (
                 len(rows), nf, nf - ns - nd, ns, FN_DESC_REL, nd), "",
             "| file | kind | imported by | functions | side file | undocumented |", "|---|---|---|---|---|---|"]
    for p, note, users, r in rows:
        lines.append("| [`%s`](#%s) | %s | %d | %d | %d | %d |" % (p, re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-"), note, len(users), len(r),
                                                                 sum(1 for x in r if x[3] == "side file"), sum(1 for x in r if x[3] == "-")))
    for p, note, users, r in rows:
        lines += ["", "### %s" % p, "", "%s; imported by %d file(s): %s%s" % (note, len(users), ", ".join("`%s`" % u for u in users[:6]),
                                                                            " ..." if len(users) > 6 else ""), ""]
        if not r:
            lines.append("(no public function)")
            continue
        lines += ["| function | arguments | what it does | from | self-test | line |", "|---|---|---|---|---|---|"]
        for name, args, text, src, st, ln in r:
            # docstring text loses its backticks: doc_lint L2 checks every backticked path, and a docstring's EXAMPLE path
            # (audit_cycle.a9_named_files: tools/x/y.py) is not a citation
            lines.append("| `%s` | %s | %s | %s | %s | %d |" % (name, _cell(args, 120), _cell(text.replace("`", "'"), 200), src, st or "-", ln))
    lines += ["", LIST_END]
    return "\n".join(lines) + "\n"


def split_list(text):
    """(before, list block, after) - block None when the list markers are absent."""
    i = text.find(LIST_BEGIN)
    if i < 0:
        return text, None, ""
    j = text.find(LIST_END, i)
    if j < 0:
        return text, None, ""
    j += len(LIST_END)
    if text[j:j + 1] == "\n":
        j += 1
    return text[:i], text[i:j], text[j:]


def put_list(text, block):
    """`text` with its fn-list block replaced by `block` (appended at the end the first time)."""
    before, old, after = split_list(text)
    if old is None:
        return text + ("" if text.endswith("\n") else "\n") + "\n" + block
    return before + block + after


# ---- the detached regeneration run (tools/hooks/guard_write.py starts it; card chat-T7 item 6(c))
STATE_DIR = os.path.join(HERE, "bench")
LOCK_NAME, RERUN_NAME, REGEN_LOG = "capabilities_regen.lock", "capabilities_regen.rerun", "capabilities_regen.log"
LOCK_STALE_S = 900


def hook_run(doc=DOC, state_dir=None, root=None):
    """`--hook-run`: the lock is ALREADY held by the hook that started this process. Regenerate; while the re-run flag exists, clear
    it and regenerate again; release the lock (re-check the flag after releasing, so a write that came in between is not lost).
    One log line per run in capabilities_regen.log. Returns the number of runs."""
    sd = state_dir or STATE_DIR
    lock, rerun, log = (os.path.join(sd, x) for x in (LOCK_NAME, RERUN_NAME, REGEN_LOG))
    runs = 0
    while True:
        while True:
            runs += 1
            try:
                if os.path.exists(rerun):
                    os.remove(rerun)
            except OSError:
                pass
            t0 = time.time()
            try:
                ch = write(doc, root=root)
                note = "%s %s" % ("rewrote" if ch else "unchanged", os.path.basename(doc))
            except Exception as e:                                                 # noqa: BLE001 - logged, never raised
                note = "FAILED %s: %s" % (type(e).__name__, str(e)[:160])
            with open(log, "a", encoding="utf-8") as f:
                f.write("CAPREGEN | %s | run %d%s | %s | %.1f s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), runs, " (re-run)" if runs > 1 else "",
                                                                   note, time.time() - t0))
            if not os.path.exists(rerun):
                break
        try:
            os.remove(lock)
        except OSError:
            pass
        if not os.path.exists(rerun):
            return runs
        try:                                                                       # a write landed after the last check: take the lock back
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except OSError:
            return runs                                                            # another run holds it and will see the flag


def summary_line(root=None):
    """'fn-table N rows; fn-list F files, M functions, S from the side file, U undocumented' - the counts cycle_runner's CAPABILITIES
    line logs."""
    lr = described_rows(root)
    return "fn-table %d rows; fn-list %d files, %d functions, %d from the side file, %d undocumented" % (
        len(rows()), len(lr), sum(len(r) for _p, _n, _u, r in lr), sum(1 for _p, _n, _u, r in lr for x in r if x[3] == "side file"),
        sum(1 for _p, _n, _u, r in lr for x in r if x[3] == "-"))


def _parse_block(block):
    d = {}
    for ln in (block or "").splitlines():
        m = ROW_RE.match(ln)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            d[m.group(1)] = cells
    return d


def drift(doc=DOC, reg_dir=None, with_list=True):
    """{'block': bool, 'missing': [...], 'gone': [...], 'stale': [...], 'record_changed': [...], 'moved': [...],
    'contract_changed': [...]} - code/registry vs the doc's generated block."""
    with open(doc, encoding="utf-8") as f:
        text = f.read()
    _b, block, _a = split(text)
    want = _parse_block(render(reg_dir))
    have = _parse_block(block)
    stale = sorted(fn for fn, c in want.items() if c[2] == "stale")
    common = sorted(set(want) & set(have))
    out = {"block": block is not None, "missing": sorted(set(want) - set(have)), "gone": sorted(set(have) - set(want)),
           "stale": stale, "record_changed": [f for f in common if want[f][2] != have[f][2]],
           "moved": [f for f in common if want[f][3] != have[f][3]],
           "contract_changed": [f for f in common if want[f][:2] != have[f][:2]]}
    if with_list:                                                                  # card chat-T7: the fn-list block too
        _b2, lblock, _a2 = split_list(text)
        out["list_block"] = lblock is not None
        out["list_stale"] = lblock is not None and lblock != render_list()
        out["stale_descriptions"] = stale_descriptions()                           # card chat-T8: side-file key of a gone function
    return out


def drift_line(d):
    """One printable line from a drift() dict ('' = no drift; doc_lint L12 prints it). Self-test: selftest_fn_f2.py."""
    if not d["block"]:
        return "the generated block is ABSENT - run py tools/gen_capabilities.py"
    parts = []
    for k in ("missing", "gone", "stale", "record_changed", "contract_changed", "moved"):
        if d[k]:
            parts.append("%s %d (%s%s)" % (k, len(d[k]), ", ".join(d[k][:5]), " ..." if len(d[k]) > 5 else ""))
    if d.get("list_block") is False:
        parts.append("fn-list block ABSENT")
    elif d.get("list_stale"):
        parts.append("fn-list block differs from the code")
    sd = d.get("stale_descriptions") or []
    if sd:
        parts.append("stale description %d in %s (%s%s)" % (len(sd), FN_DESC_REL, ", ".join(sd[:5]), " ..." if len(sd) > 5 else ""))
    return "; ".join(parts)


def main(argv=None):
    """CLI: rewrite both generated blocks (default), --check (drift, exit 1 on drift), --summary (rewrite + the counts line
    cycle_runner logs), --hook-run (the detached run guard_write starts). Returns the exit code. Self-test: selftest_t7_capabilities.py."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--doc", default=DOC)
    ap.add_argument("--hook-run", action="store_true", help="card chat-T7: the detached run guard_write starts (lock held)")
    ap.add_argument("--state-dir", default=None, help="lock / re-run flag / log directory (self-tests)")
    ap.add_argument("--summary", action="store_true", help="print the counts line cycle_runner logs")
    a = ap.parse_args(argv)
    if a.hook_run:
        n = hook_run(a.doc, a.state_dir)
        print("hook-run: %d run(s)" % n)
        return 0
    if a.summary:
        changed = write(a.doc)
        print("CAPABILITIES-SUMMARY %s | %s" % ("rewrote" if changed else "unchanged", summary_line()))
        return 0
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
