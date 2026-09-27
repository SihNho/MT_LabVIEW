"""diag_c112c_release - card 112-3 W2 (offline): which PRIOR-ART slugs of archive/peer/2026-09-27-priorart-c111e-l2b2a.md the
guard_cycle release parser (released_slugs / fixed_citations) accepts, and every rejected FIXED line with its reason."""
import os, re, sys                                                                     # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks")); sys.path.insert(0, os.path.join(ROOT, "tools"))   # noqa: E702
import guard_cycle as GC, protocol as P                                                # noqa: E401,E402
p = os.path.join(ROOT, "archive", "peer", "2026-09-27-priorart-c111e-l2b2a.md")
body = open(p, encoding="utf-8", errors="replace").read()
slugs = sorted(set(re.findall(r"^PRIOR-ART:\s*([a-z-]+)", body, re.M)))
res = GC.released_slugs(p, body)
print("VERDICT SLUGS", slugs)
print("RELEASED", res)
rel = res[0] if isinstance(res, tuple) else res
missing = [s for s in slugs if s not in set(rel)]
print(P.result_line(P.make_result(len(slugs) - len(missing), len(missing), ("unreleased: %s" % missing) if missing else None)))
