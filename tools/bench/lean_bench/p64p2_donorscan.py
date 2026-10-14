"""p64p2_donorscan - OFFLINE (no LabVIEW): search stored terminal tables for donor nodes the wrapper needs
(Unbundle By Name `code`, number<->string conversions, Concatenate Strings, Format Into String, Tick Count, Build Array).
    py tools/bench/lean_bench/p64p2_donorscan.py <json> [<json> ...]"""
import json, sys                                                                          # noqa: E401

WANT = ("code", "number", "decimal", "concatenated string", "resulting string", "millisecond timer value", "appended array",
        "format string", "string", "initial string", "output string")
for p in sys.argv[1:]:
    d = json.load(open(p, encoding="utf-8"))
    rows = d.get("rows") if isinstance(d, dict) else d
    if rows is None and isinstance(d, dict):
        rows = d.get("terminals") or next((v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
    print("==", p, type(d).__name__, len(rows or []), (list(rows[0].keys()) if rows else None))
    own = {}
    for r in rows or []:
        own.setdefault((r.get("owner_uid"), r.get("owner_class")), []).append(r.get("term_name"))
    seen = set()
    for (u, c), names in own.items():
        if c in ("SubVI", "TopLevelDiagram", "Diagram") or "Tunnel" in str(c) or "Constant" in str(c):
            continue
        key = (c, tuple(sorted(set(map(str, names)))))
        if key in seen:
            continue
        if any(str(n).lower() in WANT or "string" in str(n).lower() for n in names):
            seen.add(key)
            print(u, c, names)
