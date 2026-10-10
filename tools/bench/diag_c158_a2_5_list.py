# ---
# labview: none
# hardware: none
# ---
"""List undocumented shared-tool functions as gen_capabilities.described_rows resolves them (card 158-a2-5). Read-only; calls the
generator's helper, does not re-implement it. Prints 'path|module.fn|line|importers' rows (filtered by module names on argv) and totals."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gen_capabilities as g  # noqa: E402

tot = {}
want = sys.argv[1:]
for p, note, users, rows in g.described_rows(ROOT):
    mod = p.rsplit("/", 1)[-1][:-3]
    und = [(n, ln) for n, a, t, s, st, ln in rows if s == "-"]
    if und:
        tot[mod] = len(und)
        if not want or mod in want:
            for n, ln in und:
                print("%s|%s.%s|%s|%s" % (p, mod, n, ln, len(users)))
print("TOTALS", sorted(tot.items(), key=lambda x: -x[1]), sum(tot.values()))
