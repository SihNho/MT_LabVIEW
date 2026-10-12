# ---
# labview: none
# hardware: none
# ---
"""diag_c169_a2_2_graphs - card 169-a2-2: list tools/bench graph JSONs (file md5, header md5, Wire objs, extra keys,
note, vi, source) to choose the find_graph rule for fp-100. Read-only, pure Python.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c169_a2_2_graphs.log -- py -u tools/bench/diag_c169_a2_2_graphs.py
"""
import glob, hashlib, json, os, sys    # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol    # noqa: E402
BENCH = os.path.dirname(os.path.abspath(__file__))
n = 0
NOTE_ONLY = "--note-only" in sys.argv
pats = [a for a in sys.argv[1:] if not a.startswith("--")] or ["graph_ring_p*.json"]
for p in sorted(sum((glob.glob(os.path.join(BENCH, x)) for x in pats), [])):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except ValueError:
        continue
    if not isinstance(d, dict) or (NOTE_ONLY and "note" not in d):
        continue
    n += 1
    nw = sum(1 for o in d.get("objs", []) if isinstance(o, dict) and o.get("class") == "Wire")
    print(os.path.basename(p), hashlib.md5(open(p, "rb").read()).hexdigest()[:8], str(d.get("md5", ""))[:8], nw,
          [k for k in d if k not in ("terminals", "objs")], "|", str(d.get("note", ""))[:90], "|",
          str(d.get("vi", ""))[-45:], "|", str(d.get("source", ""))[:110])
print("files listed:", n)
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
