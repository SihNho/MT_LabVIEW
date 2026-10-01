"""c131_2_why - card 131-2: print WHY c131_2_reach v2 marks a project module's def as a COM entry (offline, reads files).
Usage: py -u tools/bench/c131_2_why.py <module.py> <name> [<name> ...]"""
import ast, os, sys                                                                 # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, B)
import c131_2_reach as R                                                            # noqa: E402

mod = os.path.normcase(os.path.abspath(os.path.join(ROOT, sys.argv[1])))
top, ent = R._info(mod)
print("module", sys.argv[1], "import_reaches", top, "entries", len(ent))
with open(mod, encoding="utf-8", errors="replace") as f:
    tree = ast.parse(f.read())
mod_nodes = list(R._walk(tree.body, True))
_h, alias, names = R._bind(mod_nodes, R._dirs(mod), frozenset())
for want in sys.argv[2:]:
    d = next((x for x in tree.body if getattr(x, "name", None) == want), None)
    if d is None:
        print(want, "not a top-level def")
        continue
    dn = list(R._walk([d], False))
    h, a2, n2 = R._bind(dn, R._dirs(mod), frozenset())
    al = dict(alias, **a2)
    why = []
    for n in dn:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            nm = [a.name for a in n.names]
            why.append("L%d import %s %s" % (n.lineno, getattr(n, "module", "") or "", nm))
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in al:
            if n.attr in R._info(al[n.value.id])[1]:
                why.append("L%d uses %s.%s (entry of %s)" % (n.lineno, n.value.id, n.attr, os.path.basename(al[n.value.id])))
        elif isinstance(n, ast.Name) and n.id in (names | n2 | ent) and n.id != want:
            why.append("L%d names entry %s" % (n.lineno, n.id))
    print(want, "entry" if want in ent else "not entry", "bind_hit", h)
    for w in why[:25]:
        print("   ", w)
