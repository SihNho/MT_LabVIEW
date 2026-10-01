"""c131_2_reach - card 131-2 P1: the CANDIDATE guard_peer offline classification (v2), as a standalone module so it is
MEASURED before it is switched on (decision docs/violation-decisions.md "device-failed - 2026-10-02 04:52"). After the
measurement passes, this exact code is copied into tools/hooks/guard_peer.py as `script_touches_labview`.

Rule (v2): a LAUNCHED script reaches LabVIEW when its code (any depth, functions included - it is what runs)
  (a) imports a LabVIEW module (gscript, stagekit, pythoncom, win32com, comtypes) or calls Dispatch("LabVIEW.Application"), or
  (b) imports a PROJECT module whose IMPORT reaches LabVIEW (module-level code only: function bodies and `if __name__`
      blocks do not run on import), or
  (c) USES a COM ENTRY of a project module it imports: `alias.name` or `from mod import name` + `name`, where an entry is
      a top-level def/class of that module whose body reaches LabVIEW by (a)-(c) (fixpoint inside the module).
An import that merely REACHES gscript through a function-local import the script never calls (fp-11, fp-22, fp-24) is
no longer LabVIEW. Fails closed: an unreadable / unparseable launched script or project module counts as reaching.
Not followed (as in v1): subprocess / importlib / runpy / exec of another file.
v1 (guard_peer.py:234-260 at md5 29a8eab3) followed EVERY `import` line by regex, function-local ones included, and
missed tools/recipes as an import directory; v2 adds tools/recipes (strictly more coverage)."""
import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LV_MODULES = frozenset(("gscript", "stagekit", "pythoncom", "win32com", "comtypes"))
# The decision's second clause ("or is a stage_prerun --dry/--prerun/self-test whose COM is stubbed",
# docs/violation-decisions.md device-failed 2026-10-02 04:52): these functions install the COM stubs themselves
# (stage_prerun.py:829-831 dry -> install(graph); :2117 prerun) and are never COM entries, whatever they import.
STUBBED_ENTRIES = {"tools/stage_prerun.py": frozenset(("dry", "prerun"))}
LV_TEXT_RE = re.compile(r"Dispatch\(\s*[\"']LabVIEW\.Application", re.I)
_MODINFO = {}


def _code_only(src):
    import protocol
    return protocol.code_only(src)


def _dirs(key):
    return [os.path.dirname(key)] + [os.path.join(ROOT, "tools", d) for d in ("", "bench", "hooks", "recipes")]


def _find(name, dirs):
    for d in dirs:
        c = os.path.join(d, name + ".py")
        if os.path.isfile(c):
            return os.path.normcase(os.path.abspath(c))
    return None


def _main_guard(n):
    return (isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
            and n.test.left.id == "__name__")


def _walk(nodes, module_level):
    """Every node under `nodes`. module_level: function/lambda BODIES and `if __name__` blocks are not entered."""
    stack = list(nodes)[::-1]
    while stack:
        n = stack.pop()
        yield n
        if module_level and (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) or _main_guard(n)):
            continue
        stack.extend(list(ast.iter_child_nodes(n))[::-1])


def _bind(nodes, dirs, stack):
    """(hit, {alias: module path}, {local names bound to an entry}) for the imports among `nodes`."""
    hit, alias, names = False, {}, set()
    for n in nodes:
        if isinstance(n, ast.Import):
            for a in n.names:
                base = a.name.split(".")[0]
                if base in LV_MODULES:
                    hit = True
                    continue
                p = _find(base, dirs)
                if p:
                    hit = hit or _info(p, stack)[0]
                    alias[a.asname or base] = p
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            base = n.module.split(".")[0]
            if base in LV_MODULES:
                hit = True
                continue
            p = _find(base, dirs)
            if p:
                top, ent = _info(p, stack)
                hit = hit or top
                for a in n.names:
                    if a.name == "*":
                        hit = hit or bool(ent)
                    elif a.name in ent:
                        names.add(a.asname or a.name)
    return hit, alias, names


def _uses(nodes, alias, names, stack):
    for n in nodes:
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in alias:
            if n.attr in _info(alias[n.value.id], stack)[1]:
                return True
        elif isinstance(n, ast.Name) and n.id in names:
            return True
    return False


def _info(path, stack=frozenset()):
    """(import_reaches, entries) of a PROJECT module. Cached per process; an import cycle contributes nothing."""
    if path in _MODINFO:
        return _MODINFO[path]
    if path in stack:
        return False, frozenset()
    stack = stack | {path}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        _MODINFO[path] = (True, frozenset())
        return _MODINFO[path]
    dirs = _dirs(path)
    code = _code_only(src)
    lv_lines = [code.count("\n", 0, m.start()) + 1 for m in LV_TEXT_RE.finditer(code)]
    try:
        stub = STUBBED_ENTRIES.get(os.path.relpath(path, ROOT).replace("\\", "/").lower(), frozenset())
    except ValueError:
        stub = frozenset()
    defs = [d for d in tree.body if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    span = {d.name: (d.lineno, d.end_lineno or d.lineno) for d in defs}
    defs = [d for d in defs if d.name not in stub]
    mod_nodes = list(_walk(tree.body, True))
    hit, alias, names = _bind(mod_nodes, dirs, stack)
    entries = {d.name for d in defs if any(span[d.name][0] <= ln <= span[d.name][1] for ln in lv_lines)}
    per_def = {}
    for d in defs:
        dn = list(_walk([d], False))
        h, a2, n2 = _bind(dn, dirs, stack)
        per_def[d.name] = (dn, h, dict(alias, **a2), names | n2)
        if h:
            entries.add(d.name)
    changed = True
    while changed:
        changed = False
        for d in defs:
            if d.name in entries:
                continue
            dn, _h, al, nm = per_def[d.name]
            if _uses(dn, al, nm | entries, stack):
                entries.add(d.name)
                changed = True
    top = hit or any(not any(s <= ln <= e for s, e in span.values()) for ln in lv_lines) \
        or _uses(mod_nodes, alias, names | entries, stack)
    _MODINFO[path] = (bool(top), frozenset(entries))
    return _MODINFO[path]


def script_touches_labview(script, _seen=None):
    """v2: True when the LAUNCHED `script` can open LabVIEW (rules in the module docstring). Fails closed."""
    key = os.path.normcase(os.path.abspath(script))
    try:
        with open(key, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        return True
    if LV_TEXT_RE.search(_code_only(src)):
        return True
    nodes = list(_walk(tree.body, False))
    stack = frozenset({key})
    hit, alias, names = _bind(nodes, _dirs(key), stack)
    return hit or _uses(nodes, alias, names, stack)
