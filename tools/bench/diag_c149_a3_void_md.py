# ---
# labview: none
# hardware: none
# ---
r"""diag_c149_a3_void_md - card 149-a3-2 step 5 write-up (OFFLINE): tools/bench/diag_c149_a3_void_census.md from the census json(s)
tools/bench/diag_c149_a3_void_<tag>.json written by diag_c149_a3_void.py (s06, s05 when present). Facts only: coverage, Void list per file,
s06-only Void entries (when both exist), the distribution of top-level type-descriptor names among the terminals read (so a reader can see
what the 'void' substring test was run against).
PREDICTION: the s06 json exists; the md is written; counts printed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c149_a3_void_md.log -- py -u tools/bench/diag_c149_a3_void_md.py"""
import collections, hashlib, json, os, sys                                                    # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(B, "diag_c149_a3_void_census.md")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
D = {}
for tag in ("s06", "s05"):
    p = os.path.join(B, "diag_c149_a3_void_%s.json" % tag)
    if os.path.isfile(p):
        D[tag] = (json.load(open(p, encoding="utf-8")), md5(p))
L = ["---", "type: facts", "status: current", "date: 2026-10-08", "card: 149-a3-2", "---",
     "# Void-type census of wire terminals (PD363(c)) - card 149-a3-2, plain gscript reads (read_terms + report_all + read_term_type), no edit verb", ""]
voids = {}
for tag, (d, m) in D.items():
    c = d.get("coverage") or {}
    T = d.get("types") or {}
    v = sorted(((int(k), x) for k, x in T.items() if x.get("void")), key=lambda t: (-t[1]["wire"], t[0]))
    voids[tag] = set((x["wire"], k, x["owner"], x["name"]) for k, x in v)
    tops = collections.Counter()
    for x in T.values():
        tds, top = x.get("tds") or [], x.get("top")
        nm = tds[top[0]] if isinstance(top, list) and top and isinstance(top[0], int) and top[0] < len(tds) else (tds[-1] if tds else "?")
        tops[nm] += 1
    L += ["## {0}: {1} (md5 {2}) - json tools/bench/diag_c149_a3_void_{0}.json md5 {3}".format(tag, os.path.basename(d["vi"]), d["md5"][:8], m),
          "- coverage: {0} of {1} wired terminals read in {2} s ({3} s/read, cap {4} s), order wire uid DESC; complete {5}; last wire read w{6}".format(
              c.get("read"), c.get("wired"), c.get("seconds"), c.get("s_per_read"), d.get("tcap_s"), c.get("complete"), c.get("last_wire")),
          "- wires covered: w{0} .. w{1} ({2} distinct)".format(max((x["wire"] for x in T.values()), default=None),
                                                             min((x["wire"] for x in T.values()), default=None), len(set(x["wire"] for x in T.values()))),
          "- Void terminals (any TD name containing 'void'): {0}; read errors: {1}".format(len(v), sum(1 for x in T.values() if x.get("err"))),
          "- NOTE gscript.TD_NAMES (tools/gscript.py:4585-4588) has no 0x00 entry, so a Void TD is named '0x00', never 'void': terminals "
          "with any TD code 0x00: {0}; with no TD at all: {1}".format(sum(1 for x in T.values() if 0 in (x.get("codes") or [])),
                                                                    sum(1 for x in T.values() if not x.get("codes"))),
          "- top-level TD name distribution of the terminals read: {0}".format(dict(tops.most_common(25))), ""]
    if v:
        L += ["| wire | term | src | owner | class | name | TDs |", "|---|---|---|---|---|---|---|"]
        L += ["| {0} | {1} | {2} | {3} | {4} | {5!r} | {6} |".format(x["wire"], k, x["src"], x["owner"], x["cls"], x["name"], x["tds"]) for k, x in v]
        L.append("")
if "s05" not in D:
    L += ["## s05 (byte copy of D1_ring_p4s05_20261008_002621.vi 3f9ac26b): NOT RUN - the card returned at the s06 run's COV gate FAIL "
          "(first unexpected result, card chat-P2); s06-only list therefore not computable.", ""]
else:
    only = sorted(voids.get("s06", set()) - voids.get("s05", set()), key=lambda t: -t[0])
    L += ["## s06-only Void entries (wire, term, owner, name not in s05's list): {0}".format(len(only))] + ["- {0}".format(o) for o in only] + [""]
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L), flush=True)
ok = "s06" in D
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "no s06 json", [{"path": "tools/bench/diag_c149_a3_void_census.md", "md5": md5(OUT)}])), flush=True)
sys.exit(0 if ok else 1)
