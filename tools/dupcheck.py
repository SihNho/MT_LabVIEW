# ---
# labview: none
# hardware: none
# ---
"""dupcheck.py - duplicate-code finder: blocks of >= MIN logical lines (default 8) that appear in >= 2 files after
normalisation (card chat-L1, user 2026-10-09; the rule it serves is docs/script-writing.md rule 1 "logic lives once").

Normalisation (normalize()): Python tokenize; comments, blank lines, indentation, import statements and lone string
expressions (docstrings) are dropped; every number literal -> 0 and every string literal (incl. f-strings) -> S;
identifiers and operators are kept. One normalised line = one LOGICAL line (so a call wrapped over 4 physical lines
counts once). Windows of MIN consecutive normalised lines are hashed; a window found in >= 2 distinct files is a
duplicate; consecutive duplicate windows with the same partner set are merged into one block (find_blocks()).

Scope (default_files()): tools/*.py, tools/hooks/*.py, tools/recipes/*.py and the shared bench files listed in
tools/bench/capabilities_shared.json. Folder classes come from tools/lint.py classify() (called, not copied).
A block whose copies are ALL in tools/recipes is reported in the separate "recipe-only" group (old recipes are records).

Usage:
  py tools/dupcheck.py [--min 8] [--top 40] [--json out.json]   ranked table (copies x size) + RESULT line
  py tools/dupcheck.py --self-test                              synthetic sources in memory, no project scan
Existing tooling checked first: no clone detector in tools/ (grep -l "tokenize" tools/*.py -> scope_header/guard_write
use tokenize only for header/compile checks); tools/lint.py (this card) owns the folder classes.
"""
import argparse
import ast
import hashlib
import io
import json
import os
import sys
import tempfile
import tokenize
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint  # noqa: E402  (folder classes: lint.classify / lint.load_shared / lint.norm)

ROOT = lint.ROOT
_SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER}


def normalize(text):
    """List of (normalised logical line, first physical line, last physical line) for Python source `text`.
    Returns [] on a tokenize error. Self-test: --self-test."""
    out, cur, start = [], [], None
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return []
    for t in toks:
        if t.type in _SKIP:
            continue
        if t.type == tokenize.NEWLINE:
            if cur:
                line = " ".join(cur)
                if not (line.startswith(("import ", "from ")) or line == "S"):
                    out.append((line, start, t.start[0]))
            cur, start = [], None
            continue
        if start is None:
            start = t.start[0]
        if t.type == tokenize.NUMBER:
            cur.append("0")
        elif t.type == tokenize.STRING:
            if not (cur and cur[-1] == "S"):       # implicit concatenation "a" "b" -> one S
                cur.append("S")
        else:
            cur.append(t.string)
    return out


def enclosing_defs(text):
    """Sorted [(first line, last line, name)] of every def/class in `text` (for the 'where' column). Self-test: --self-test."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return sorted((n.lineno, getattr(n, "end_lineno", n.lineno), n.name) for n in ast.walk(tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))


def where(defs, line):
    """Innermost def/class name containing `line`, or '<module>'. Self-test: --self-test."""
    best = None
    for a, b, name in defs:
        if a <= line <= b and (best is None or a >= best[0]):
            best = (a, name)
    return best[1] if best else "<module>"


def find_blocks(sources, min_lines=8):
    """Duplicate blocks across `sources` {path: text}. Returns a list of dicts {size, copies: [{path, start, end, where}],
    files, first} where size = normalised logical lines, sorted by copies x size descending. Self-test: --self-test."""
    norm = {p: normalize(t) for p, t in sources.items()}
    defs = {p: enclosing_defs(t) for p, t in sources.items()}
    hashes, occ = {}, defaultdict(list)
    for p, lines in norm.items():
        hs = []
        for i in range(len(lines) - min_lines + 1):
            h = hashlib.md5("\n".join(x[0] for x in lines[i:i + min_lines]).encode("utf-8")).hexdigest()
            hs.append(h)
            occ[h].append((p, i))
        hashes[p] = hs
    dup = {h: tuple(sorted(o)) for h, o in occ.items() if len({p for p, _ in o}) >= 2}
    blocks, seen = [], set()
    for p in sorted(hashes):
        hs = hashes[p]
        i = 0
        while i < len(hs):
            o = dup.get(hs[i])
            if o is None:
                i += 1
                continue
            j = i
            while j + 1 < len(hs) and dup.get(hs[j + 1]) == tuple(sorted((q, k + 1) for q, k in dup[hs[j]])):
                j += 1
            key = (o, j - i)                         # the same block seen from each partner file has the same key
            if key not in seen:
                seen.add(key)
                n_win = j - i
                copies = []
                for q, k in o:
                    ln = norm[q]
                    copies.append({"path": lint.norm(q), "start": ln[k][1], "end": ln[k + n_win + min_lines - 1][2],
                                   "where": where(defs[q], ln[k][1])})
                blocks.append({"size": n_win + min_lines, "copies": copies,
                               "files": len({c["path"] for c in copies}), "first": norm[o[0][0]][o[0][1]][0][:100]})
            i = j + 1
    blocks.sort(key=lambda b: (-len(b["copies"]) * b["size"], -b["size"]))
    return blocks


def default_files(root=ROOT):
    """Project-relative scope list: tools/*.py, tools/hooks/*.py, tools/recipes/*.py + shared bench files."""
    out = []
    for sub in ("tools", "tools/hooks", "tools/recipes"):
        d = os.path.join(root, sub)
        out += [sub + "/" + f for f in sorted(os.listdir(d)) if f.endswith(".py")]
    out += sorted(p for p in lint.load_shared() if p.startswith("tools/bench/"))
    return sorted(set(out))


def group_of(block):
    """'recipe-only' when every copy is in tools/recipes, else 'main'. Self-test: --self-test."""
    return "recipe-only" if all(c["path"].startswith("tools/recipes/") for c in block["copies"]) else "main"


def table(blocks, top):
    """Markdown table of the first `top` blocks. Returns str."""
    out = ["| # | copies x size | files | copies (path:start-end, def) | first line |", "|---:|---:|---:|---|---|"]
    for n, b in enumerate(blocks[:top], 1):
        cs = "<br>".join("%s:%d-%d `%s`" % (c["path"], c["start"], c["end"], c["where"]) for c in b["copies"])
        out.append("| %d | %d x %d | %d | %s | `%s` |" % (n, len(b["copies"]), b["size"], b["files"], cs,
                                                       b["first"].replace("|", "\\|")))
    return "\n".join(out)


def self_test():
    body = ("def f{n}(a, b):\n    # comment {n}\n    x = a + {n}\n    y = b * 2.5\n    if x > y:\n        z = 'one{n}'\n"
            "    else:\n        z = \"two\"\n    w = [x, y,\n         z]\n    print(w)\n    return w, {n}\n")
    short = "def g():\n    a = 1\n    b = 2\n    c = a + b\n    d = c * 2\n    e = d - 1\n    return e\n"
    tmp = tempfile.gettempdir()                   # paths only; nothing is written
    srcs = {os.path.join(tmp, "a.py"): "import os\n" + body.format(n=1) + short,
            os.path.join(tmp, "b.py"): "import sys\nfrom x import y\n" + body.format(n=7),
            os.path.join(tmp, "c.py"): short}
    blocks = find_blocks(srcs, 8)
    nl = normalize(body.format(n=3))
    defs = enclosing_defs(body.format(n=3))
    checks = [
        ("normalised logical lines of body (comment dropped)", len(nl) == 10),
        ("wrapped list is one logical line", any(x[0] == "w = [ x , y , z ]" and x[2] - x[1] == 1 for x in nl)),
        ("literals -> placeholders", nl[1][0] == "x = a + 0" and nl[2][0] == "y = b * 0" and nl[4][0] == "z = S"),
        ("exactly one block", len(blocks) == 1),
        ("block size 9 (def lines f1/f7 differ, imports ignored)", blocks and blocks[0]["size"] == 9),
        ("two files", blocks and blocks[0]["files"] == 2),
        ("7-line short function not reported", not any(b["size"] < 8 for b in blocks)),
        ("where = enclosing def", blocks and {c["where"] for c in blocks[0]["copies"]} == {"f1", "f7"}),
        ("where() module", where(defs, 999) == "<module>"),
        ("group_of recipe-only", group_of({"copies": [{"path": "tools/recipes/a.py"}, {"path": "tools/recipes/b.py"}]})
         == "recipe-only" and group_of({"copies": [{"path": "tools/recipes/a.py"}, {"path": "tools/x.py"}]}) == "main"),
        ("tokenize error -> []", normalize("def f(:\n  (\n") == []),
    ]
    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        if not c:
            print("FAIL", name)
    return ok, len(checks) - ok


def main():
    import protocol
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=8)
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        ok, fail = self_test()
        print("SELFTEST dupcheck.py %d/%d" % (ok, fail))
        print(protocol.result_line(protocol.make_result(ok, fail, None if not fail else "dupcheck self-test")))
        return 1 if fail else 0
    files = default_files()
    sources = {}
    for p in files:
        with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as f:
            sources[os.path.join(ROOT, p)] = f.read()
    blocks = find_blocks(sources, a.min)
    main_b = [b for b in blocks if group_of(b) == "main"]
    rec_b = [b for b in blocks if group_of(b) == "recipe-only"]
    print("SCOPE %d files; %d duplicate blocks (main %d, recipe-only %d), min %d logical lines"
          % (len(files), len(blocks), len(main_b), len(rec_b), a.min))
    print("## main\n" + table(main_b, a.top))
    print("## recipe-only\n" + table(rec_b, a.top))
    arts = []
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"schema": "dupcheck/1", "min": a.min, "files": len(files), "main": main_b, "recipe_only": rec_b},
                      f, indent=1)
        arts = [{"path": lint.norm(a.json), "md5": hashlib.md5(open(a.json, "rb").read()).hexdigest()}]
    print(protocol.result_line(protocol.make_result(1, 0, artefacts=arts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
