# ---
# labview: none
# hardware: none
# ---
r"""diag_c149_a1_3_cmp - card 149-a1-3 OFFLINE: compare the measured s05 terminal table (graph_ring_p4s05_20261008_013759.json, md5
header 3f9ac26b, card 147-a1-1) with the s06 table read by diag_c149_a1_3_wire.py (diag_c149_a1_3_wire.json). For every s05 wire that
has sinks but NO source (the class of s05 EL item 7 and, by its detail text, items 10/11) and every s05 wire with a loop-tunnel sink:
its sink terminals in s05, which wire each sink terminal is on in s06 and that wire's source(s) in s06. Also the s06-only sourceless
wires. Reads JSON only. PREDICTION: none (a listing); RESULT line printed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c149_a1_3_cmp.log -- py -u tools/bench/diag_c149_a1_3_cmp.py"""
import hashlib, json, os, sys                                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, ROOT)
from tools import protocol                                                                    # noqa: E402
S05 = json.load(open(os.path.join(HERE, "graph_ring_p4s05_20261008_013759.json"), encoding="utf-8"))
S06 = json.load(open(os.path.join(HERE, "diag_c149_a1_3_wire.json"), encoding="utf-8"))


def table(rows):
    by = {}
    term = {}
    for r in rows:
        term[int(r["term_uid"])] = r
        k = int(r.get("wire_uid") or 0)
        if k:
            by.setdefault(k, []).append(r)
    return by, term


b5, t5 = table(S05["terminals"])
b6, t6 = table(S06["terminals"])
print("s05 rows %d wires-with-terms %d | s06 rows %d wires-with-terms %d" % (len(t5), len(b5), len(t6), len(b6)))


def desc(r):
    return "t%s %r %s #%s(%s)" % (r["term_uid"], r["term_name"], "SRC" if r["is_source"] else "snk", r["owner_uid"], r["owner_class"])


def nosrc(by):
    return sorted(k for k, rs in by.items() if not any(r["is_source"] for r in rs))


n5, n6 = nosrc(b5), nosrc(b6)
print("s05 sinks-but-no-source wires %d %s" % (len(n5), n5))
print("s06 sinks-but-no-source wires %d %s" % (len(n6), n6))
for k in n5:
    print("S05-NOSRC w%s:" % k)
    for r in b5[k]:
        r6 = t6.get(int(r["term_uid"]))
        w6 = int((r6 or {}).get("wire_uid") or 0)
        srcs = [desc(x) for x in b6.get(w6, []) if x["is_source"]] if w6 else []
        print("   %s | s06: %s wire %s, s06 sources %s" % (desc(r), "present" if r6 else "ABSENT", w6, srcs))
for k in n6:
    if k not in n5:
        print("S06-ONLY-NOSRC w%s: %s" % (k, [desc(r) for r in b6[k]]))
multi5 = sorted(k for k, rs in b5.items() if sum(1 for r in rs if r["is_source"]) > 1)
multi6 = sorted(k for k, rs in b6.items() if sum(1 for r in rs if r["is_source"]) > 1)
print("multi-source wires s05 %s s06 %s" % (multi5, multi6))
gone = sorted(set(b5) - set(b6))
new = sorted(set(b6) - set(b5))
print("wires (with terms) only in s05: %d %s" % (len(gone), gone))
print("wires (with terms) only in s06: %d %s" % (len(new), new))
for k in gone:
    print("  GONE w%s: %s" % (k, [desc(r) for r in b5[k]]))
for k in new:
    print("  NEW  w%s: %s" % (k, [desc(r) for r in b6[k]]))
w5 = set(int(o["uid"]) for o in S05.get("objs", []) if o.get("class") == "Wire")
w6 = set(int(u) for u in S06["wire_uids"])
tl5, tl6 = sorted(w5 - set(b5)), sorted(w6 - set(b6))
print("Wire objects s05 %d s06 %d | termless s05 %d %s | termless s06 %d %s" % (len(w5), len(w6), len(tl5), tl5, len(tl6), tl6))
print("termless only in s06 %s ; only in s05 %s" % (sorted(set(tl6) - set(tl5)), sorted(set(tl5) - set(tl6))))
ns5 = sorted(k for k, rs in b5.items() if not any(not r["is_source"] for r in rs))
ns6 = sorted(k for k, rs in b6.items() if not any(not r["is_source"] for r in rs))
print("source-but-no-sink s05 %s s06 %s" % (ns5, ns6))
for k in sorted(set(ns5) ^ set(ns6)):
    print("  NOSINK-DIFF w%s s05 %s | s06 %s" % (k, [desc(r) for r in b5.get(k, [])], [desc(r) for r in b6.get(k, [])]))
    for r in b5.get(k, []):
        r6 = t6.get(int(r["term_uid"]))
        print("     s05 term %s -> s06 wire %s" % (desc(r), (r6 or {}).get("wire_uid")))
print(protocol.result_line(protocol.make_result(1, 0, None, [{"path": "tools/bench/diag_c149_a1_3_wire.json", "md5": hashlib.md5(
    open(os.path.join(HERE, "diag_c149_a1_3_wire.json"), "rb").read()).hexdigest()}])), flush=True)
