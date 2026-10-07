# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_2_build_table - card 145-a2-2 (PD351(c)), OFFLINE: builds tools/bench/subvi_requiredness.json, the MEASURED
connector-pane requiredness table elrule reads for a created SubVI call, from the facts file of card 145-a2-3/145-a2-4
(tools/bench/diag_c145_a2_3_facts.md:10-33, reader OpWiringRules_v0, positive control PASS) - nothing else is a source.
Prior art checked: no requiredness table existed (grep 'requiredness' tools/ -> none); elrule.py had no SubVI branch.
PREDICTION CONTRACT:
  T1 the facts table parses to exactly 24 rows, 12 per VI, pane index 0..11 contiguous for each of RingPickSlot_v0 / RingSeqCheck_v0
  T2 every row's rule agrees with the measure log's rule vector (diag_c145_a2_3_measure.log:5 and :18)
  T3 each VI's file md5 on disk starts with the short md5 pinned by the measure log (:34): 6fcf153f / 0295a8d3
  T4 no terminal is Required (rule 1) - the measured fact (facts :10-33)
  T5 the facts file md5 == 1bea567336db4e797869c533940aae0b (card input pin)
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c145_a2_2_build_table.log -- py -u tools/bench/diag_c145_a2_2_build_table.py"""
import hashlib, json, os, re, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
FACTS = "tools/bench/diag_c145_a2_3_facts.md"
MLOG = "tools/bench/diag_c145_a2_3_measure.log"
OUT = "tools/bench/subvi_requiredness.json"
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PIN = {"RingPickSlot_v0": "6fcf153f", "RingSeqCheck_v0": "0295a8d3"}
VEC = {"RingPickSlot_v0": [0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2], "RingSeqCheck_v0": [0, 2, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2]}  # measure log :5, :18
MEANING = {0: "Invalid", 1: "Required", 2: "Recommended", 3: "Optional"}
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                # noqa: E731
fp = os.path.join(ROOT, FACTS)
gate("T5 facts md5 pinned", md5(fp) == "1bea567336db4e797869c533940aae0b", md5(fp))
row_re = re.compile(r"^\| (Ring\w+_v0) \| (\d+) \| ([^|]*?) ?\| (\d) \| (\w+) \| (\w+) \| (\w+) \|$")
vis = {}
for ln, line in enumerate(open(fp, encoding="utf-8"), 1):
    m = row_re.match(line.rstrip("\n"))
    if not m:
        continue
    vi, idx, name, rule, meaning, dr, wired = m.groups()
    vis.setdefault(vi, []).append({"index": int(idx), "name": name.strip(), "rule": int(rule), "meaning": meaning, "dir": dr,
                                   "wired_at_s04": {"True": True, "False": False}.get(wired), "src": "{0}:{1}".format(FACTS, ln)})
gate("T1 24 rows, 12 per VI, index 0..11", sorted(vis) == sorted(PIN) and all([t["index"] for t in vis[v]] == list(range(12)) for v in vis),
     dict((v, len(t)) for v, t in vis.items()))
gate("T2 rules == measure log vectors", all([t["rule"] for t in vis.get(v, [])] == VEC[v] for v in VEC),
     dict((v, [t["rule"] for t in vis.get(v, [])]) for v in VEC))
full = {}
for v in PIN:
    p = os.path.join(CLAUDEDEV, v + ".vi")
    full[v] = md5(p) if os.path.exists(p) else None
gate("T3 VI md5 on disk == pinned short md5", all((full[v] or "").startswith(PIN[v]) for v in PIN), full)
gate("T4 no terminal measured Required (rule 1)", all(t["rule"] != 1 for v in vis for t in vis[v]),
     [(v, t["index"]) for v in vis for t in vis[v] if t["rule"] == 1])
doc = {"schema": "subvi-requiredness/1", "card": "145-a2-2", "pd": "PD351(c)",
       "what": "connector-pane wiring rule per terminal (0 Invalid = free slot, 1 Required, 2 Recommended, 3 Optional), MEASURED by "
               "OpWiringRules_v0 (card 145-a2-4); tools/elrule.py counts an unwired input of a created SubVI as an Error List item "
               "ONLY when its rule here is 1; a VI or terminal missing here is 'uncertain' (reported, never counted)",
       "source": {"facts": FACTS, "facts_md5": md5(fp), "facts_lines": "10-33", "log": MLOG, "log_md5": md5(os.path.join(ROOT, MLOG)),
                  "log_lines": {"RingPickSlot_v0": "5-17", "RingSeqCheck_v0": "18-30", "pins": "34"}},
       "vis": dict((v + ".vi", {"md5": full[v], "md5_pinned": PIN[v], "terminals": vis[v]}) for v in sorted(vis))}
if not G["fail"]:
    json.dump(doc, open(os.path.join(ROOT, OUT), "w", encoding="utf-8"), indent=1)
    print("WROTE {0} md5 {1}".format(OUT, md5(os.path.join(ROOT, OUT))), flush=True)
arts = [{"path": OUT, "md5": md5(os.path.join(ROOT, OUT))}] if not G["fail"] else []
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], arts)), flush=True)
sys.exit(1 if G["fail"] else 0)
