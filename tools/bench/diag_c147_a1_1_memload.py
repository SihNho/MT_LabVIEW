# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_1_memload - card 147-a1-1 step 5 (OFFLINE, no LabVIEW): add ONE entry to tools/bench/memory_model.json `load_by_vi`, keyed by the
adopted s05 file's md5 3f9ac26b, value = the measured load MB from tools/bench/diag_c147_a1_1_graph.log ("MEM after load: X MB private", the
meter every load_by_vi entry cites, e.g. diag_c145_2_graph.log:24). Entry form copied from the 95e408ff entry (memory_model.json:64-68).
Nothing else changes: the old and new JSON are diffed key by key (flattened paths) and the ONLY difference must be the one added key.
The file is rewritten with the same json.dump indent as found (1) so untouched lines stay byte-identical; a text diff is reported too.
PREDICTION CONTRACT: M exactly one 'MEM after load' line in the graph log; K md5 3f9ac26b not yet a key; D flattened diff == {added: the 3 leaf
  paths of the new entry, removed: [], changed: []}; T text diff = inserted lines (+ one '}' -> '},').
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_1_memload.log -- py -u tools/bench/diag_c147_a1_1_memload.py"""
import copy, difflib, hashlib, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
MM = os.path.join(B, "memory_model.json")
LOG = os.path.join(B, "diag_c147_a1_1_graph.log")
KEY = "3f9ac26b69179eb53c202d90407ce7ee"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
        sys.exit(1)


def flat(o, p=""):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            out.update(flat(v, p + "/" + str(k)))
        return out or {p: {}}
    if isinstance(o, list):
        out = {}
        for i, v in enumerate(o):
            out.update(flat(v, p + "[" + str(i) + "]"))
        return out or {p: []}
    return {p: o}


lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
hits = [(i, ln) for i, ln in enumerate(lines, 1) if "MEM after load:" in ln]
gate("M exactly one 'MEM after load' line in the graph log", len(hits) == 1, hits)
ln_no, ln = hits[0]
val = float(re.search(r"MEM after load: ([0-9.]+) MB private", ln).group(1))
old_text = open(MM, encoding="utf-8").read()
old_md5 = md5(MM)
old = json.loads(old_text)
gate("K md5 3f9ac26b not yet a load_by_vi key", KEY not in old["load_by_vi"], list(old["load_by_vi"]))
new = copy.deepcopy(old)
new["load_by_vi"][KEY] = {"value": val,
                          "vi": "claudeDev\\D1_ring_p4s05_20261008_002621.vi (P4 v18 session 5 ADOPTED file without a rerun, card 147-a1-1; PD354(c), PD353(d))",
                          "cite": "tools/bench/diag_c147_a1_1_graph.log:{0} (MEM after load: {1} MB private)".format(ln_no, val)}
fo, fn = flat(old), flat(new)
added = sorted(set(fn) - set(fo))
removed = sorted(set(fo) - set(fn))
changed = sorted(k for k in set(fo) & set(fn) if fo[k] != fn[k])
gate("D flattened key-by-key diff: only the 3 leaves of load_by_vi/{0} added".format(KEY[:8]),
     added == sorted("/load_by_vi/{0}/{1}".format(KEY, k) for k in ("cite", "value", "vi")) and not removed and not changed,
     {"added": added, "removed": removed, "changed": changed})
new_text = json.dumps(new, indent=1, ensure_ascii=False) + ("\n" if old_text.endswith("\n") else "")
gate("F re-dump of the OLD object reproduces the old file byte for byte (so only the new entry's lines differ)",
     json.dumps(old, indent=1, ensure_ascii=False) + ("\n" if old_text.endswith("\n") else "") == old_text)
dl = [d for d in difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm="", n=0) if d[:1] in "+-" and d[:3] not in ("+++", "---")]
mins = [d[1:] for d in dl if d.startswith("-")]
plus = [d[1:] for d in dl if d.startswith("+")]
gate("T text diff = inserted lines + the previous last entry's closing brace gaining its comma (JSON syntax)",
     dl and all(m + "," in plus for m in mins) and len(mins) <= 1, dl)
open(MM, "w", encoding="utf-8").write(new_text)
for d in dl:
    print("DIFF {0}".format(d), flush=True)
print("FACT memory_model.json md5 {0} -> {1}; added key load_by_vi/{2} value {3} (cite log :{4})".format(old_md5, md5(MM), KEY, val, ln_no), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": "tools/bench/memory_model.json", "md5": md5(MM)}])), flush=True)
sys.exit(0)
