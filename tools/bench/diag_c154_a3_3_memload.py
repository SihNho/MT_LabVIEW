# ---
# labview: none
# hardware: none
# ---
r"""diag_c154_a3_3_memload - card 154-a3-3b (OFFLINE, no LabVIEW): add ONE entry to tools/bench/memory_model.json `load_by_vi`,
keyed by the adopted P5-1a file's md5 (diag_c154_p5s01a_scratch_sum.json final_md5), value = the measured load MB from
tools/bench/diag_c154_a3_3_graph.log ("MEM after load: X MB private", the meter every load_by_vi entry cites). COPIED from
tools/bench/diag_c152_b3_1_memload.py (c63a0a06, card 152-b3-1, ran 5/0) with the card id / graph log / scratch log / step name changed
(names only; the calibration print's pred start 595.0 -> the P5-1a pred start 602.6, brief_154-a3-3.md:17); calibration facts from the scratch
log's LAST segment. Changed lines: 5-13, 20-21, 23, 62-63, 83.
Nothing else changes: old and new JSON diffed key by key (flattened paths); the ONLY difference must be the one added key.
PREDICTION CONTRACT: M exactly one 'MEM after load' line in the graph log; K the P5-1a md5 not yet a key; D flattened diff == {added: the 3 leaf
  paths of the new entry, removed: [], changed: []}; F re-dump reproduces the old file; T text diff = inserted lines (+ one '}' -> '},').
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c154_a3_3_memload.log -- py -u tools/bench/diag_c154_a3_3_memload.py"""
import copy, difflib, hashlib, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
MM = os.path.join(B, "memory_model.json")
LOG = os.path.join(B, "diag_c154_a3_3_graph.log")
SUM = json.load(open(os.path.join(B, "diag_c154_p5s01a_scratch_sum.json"), encoding="utf-8"))
KEY, VIN = SUM["final_md5"], os.path.basename(SUM["final"])
START_ASSUMED = 602.6
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
gate("K md5 {0} not yet a load_by_vi key".format(KEY[:8]), KEY not in old["load_by_vi"], list(old["load_by_vi"]))
new = copy.deepcopy(old)
new["load_by_vi"][KEY] = {"value": val,
                          "vi": "claudeDev\\{0} (P5-1a ADOPTED scratch work copy, card 154-a3-3b; PD329(a), PD354(a), PD374(e)(f), PD376)".format(VIN),
                          "cite": "tools/bench/diag_c154_a3_3_graph.log:{0} (MEM after load: {1} MB private)".format(ln_no, val)}
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
slog = open(os.path.join(B, "diag_c154_p5s01a_scratch.log"), encoding="utf-8", errors="replace").read().splitlines()
seg0 = max(i for i, l in enumerate(slog) if l.startswith("BGRUN START"))
st = [(i, l) for i, l in enumerate(slog, 1) if i - 1 >= seg0 and re.search(r"METER start\s+k\s+0\s+private", l)]
st_mb = float(re.search(r"private ([\d.]+) MB", st[0][1]).group(1)) if st else None
mbs = [(i, float(m.group(1))) for i, l in enumerate(slog, 1) if i - 1 >= seg0
       for m in [re.search(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", l)] if m]
pk = max(mbs, key=lambda t: t[1]) if mbs else (None, None)
print("FACT calibration (no coefficient changed): metered scratch start {0} MB (scratch log :{1}) vs pred start {2} (d {3}); "
      "last-segment peak {4} MB (:{5}) vs X10 {6} (d {7}); sum peak_mb (whole file) {8}".format(
          st_mb, st[0][0] if st else None, START_ASSUMED, None if st_mb is None else round(st_mb - START_ASSUMED, 1), pk[1], pk[0], SUM.get("x10"),
          None if pk[1] is None or SUM.get("x10") is None else round(pk[1] - SUM["x10"], 1), SUM.get("peak_mb")), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": "tools/bench/memory_model.json", "md5": md5(MM)}])), flush=True)
sys.exit(0)
